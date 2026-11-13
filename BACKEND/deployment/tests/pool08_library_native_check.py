"""Real owned native media stores: rollback, quota, revocation and byte-integrity checks."""
import runpy,unittest,importlib,uuid,json,base64,io
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
from PIL import Image
f=runpy.run_path(str(Path(__file__).with_name('pool08_landings_native_check.py')),run_name='library_native_setup')
from django.db import connection
from django.http import QueryDict
from django.utils import timezone as dtime
from apps.turismo.models import VerifiedCompanyLink
from rest_framework.test import APIRequestFactory,force_authenticate
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 models=importlib.import_module(path+'.library_models')
 with connection.schema_editor() as editor:
  for model in (models.LibraryItem,models.LibraryEvent,models.LibraryBlob):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)
def cases(system,path):
 api=importlib.import_module(path+'.crm_api');models=importlib.import_module(path+'.library_models');domain=importlib.import_module(path+'.media_library')
 class Checks(unittest.TestCase):
  def setUp(self):
   self.c=f['cases'](system,path)();self.c.setUp();self.addCleanup(self.c.doCleanups);b=io.BytesIO();Image.new('RGB',(40,20)).save(b,format='PNG');self.raw=b.getvalue();self.meta={'title':'Marca propia','classification':'MARKETING','brand':{'name':'Empresa','tagline':'Lema','template':'SQUARE'},'rights':{'holder':'Titular','license':'OWNED','reference':'Declarada de prueba','valid_until':(datetime.now(timezone.utc)+timedelta(hours=1)).isoformat(),'public_web':True}}
  def body(self):return {'request_id':str(uuid.uuid4()),'item_id':None,'expected_revision':0,'metadata':self.meta}
  def engine(self):
   q=QueryDict(mutable=True);q['provider_id']=str(self.c.c.base.provider.pk);return api.library_api.service(api.CRMView().service(SimpleNamespace(method='POST',query_params=q,user=self.c.c.base.user)))
  def upload(self):return self.engine().upload(self.body(),self.raw,'image/png')['item_id']
  def get(self,ref,section='list',version=None,kind=None):
   r=APIRequestFactory().get('/fixture/?provider_id='+str(self.c.c.base.provider.pk));force_authenticate(r,user=self.c.c.base.user);return api.LibraryView.as_view()(r,item_id=ref,section=section,**({'version':version,'kind':kind} if version else {}))
  def command(self,ref,op,rev,**data):return self.engine().command({'request_id':str(uuid.uuid4()),'item_id':ref,'operation':op,'expected_revision':rev,'data':data})
  def public(self,ref):return api.PublicLibraryView.as_view()(APIRequestFactory().get('/public/'),item_id=ref,version=1)
  def publish(self,ref):self.command(ref,'approve',1,rights_confirmed=True,privacy_reviewed=True);self.command(ref,'publish',2,confirmed=True)
  def test_audit_failure_rolls_back_original_derivative_and_item(self):
   with patch.object(models.LibraryEvent.objects,'create',side_effect=RuntimeError('synthetic audit unavailable')):
    with self.assertRaises(RuntimeError):self.upload()
   self.assertEqual(models.LibraryItem.objects.filter(scope=str(self.c.c.base.tenant.pk)).count(),0);self.assertEqual(models.LibraryBlob.objects.filter(scope=str(self.c.c.base.tenant.pk)).count(),0)
  def test_usage_counts_both_bytes_and_quota_prevents_new_blob(self):
   lib=self.engine();ref=lib.upload(self.body(),self.raw,'image/png')['item_id'];v=lib.get(ref)['versions'][0];self.assertEqual(lib.store.usage(),(1,v['original_size']+v['delivery_size']))
   with patch.object(lib.store,'usage',return_value=(200,0)):
    with self.assertRaises(domain.CRMError) as error:lib.upload(self.body(),self.raw,'image/png')
    self.assertEqual(error.exception.status,413)
   self.assertEqual(models.LibraryBlob.objects.filter(scope=str(self.c.c.base.tenant.pk)).count(),1)
  def test_revoked_company_prevents_read_and_public_bytes(self):
   ref=self.upload();self.publish(ref);VerifiedCompanyLink.objects.filter(pk=self.c.c.base.link.pk).update(revoked_at=dtime.now());self.assertEqual(self.get(ref).status_code,403);self.assertEqual(self.public(ref).status_code,404)
  def test_corrupt_derivative_is_not_returned_or_published(self):
   ref=self.upload();self.publish(ref);v=self.engine().get(ref)['versions'][0];models.LibraryBlob.objects.filter(pk=v['blob_id']).update(delivery=b'corrupt');self.assertEqual(self.get(ref,'bytes',1,'delivery').status_code,503);self.assertEqual(self.public(ref).status_code,404);original=self.get(ref,'bytes',1,'original');self.assertEqual(original.status_code,200);self.assertEqual(original.content,self.raw)
  def test_expiry_after_publication_blocks_anonymous_response(self):
   ref=self.upload();self.publish(ref)
   class Clock:
    @staticmethod
    def now(tz):return datetime.now(timezone.utc)+timedelta(days=1)
   with patch.object(domain,'datetime',Clock):self.assertEqual(self.public(ref).status_code,404)
  def test_metadata_revision_does_not_replace_original(self):
   ref=self.upload();lib=self.engine();first=lib.bytes(ref,1,'original')[0];changed={**self.meta,'title':'Revisado'};self.command(ref,'revise',1,**changed);self.assertEqual(lib.bytes(ref,1,'original')[0],first);self.assertEqual(lib.bytes(ref,2,'original')[0],first);self.assertEqual(lib.store.usage()[0],1)
 Checks.__name__=system.replace('-','')+'Library';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
