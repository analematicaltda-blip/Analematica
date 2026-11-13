"""Own ORM: rollback, revoked links, scope isolation and private receipt integrity."""
import runpy,unittest,importlib,uuid,os
from pathlib import Path
from unittest.mock import patch
f=runpy.run_path(str(Path(__file__).with_name('pool08_crm_native_check.py')),run_name='landing_native_setup')
from django.db import connection
from django.utils import timezone
from apps.turismo.models import VerifiedCompanyLink
from rest_framework.test import APIRequestFactory,force_authenticate
for p in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 models=importlib.import_module(p+'.landing_models')
 with connection.schema_editor() as editor:
  for m in (models.CommercialLanding,models.LandingEvent):
   if m._meta.db_table not in connection.introspection.table_names():editor.create_model(m)
def cases(system,path):
 api=importlib.import_module(path+'.crm_api');models=importlib.import_module(path+'.landing_models')
 class Checks(unittest.TestCase):
  def setUp(self):
   self.c=f['cases'](system,path)();self.c.setUp();self.addCleanup(self.c.doCleanups);self.ref=None
  def body(self):return dict(request_id=str(uuid.uuid4()),operation='create',landing_id=None,expected_revision=0,data={'slug':'pagina-'+uuid.uuid4().hex,'content':{'brand':'Propia','title':'Página','description':'Servicios','template':'SERVICIOS','blocks':[{'kind':'TEXT','heading':'Hola','body':'','url':'','label':''}]}})
  def call(self,body=None,ref=None,section='list',user=None):
   url='/fixture/?provider_id='+str(self.c.base.provider.pk);req=APIRequestFactory().post(url,body,format='json') if body else APIRequestFactory().get(url);force_authenticate(req,user=user or self.c.base.user);return api.LandingsView.as_view()(req,**({'item_id':ref} if ref else {}),section=section)
  def test_revocation_rejects_read_command_and_receipt_recovery(self):
   b=self.body();r=self.call(b);self.assertEqual(r.status_code,200,r.data);ref=r.data['landing_id'];VerifiedCompanyLink.objects.filter(pk=self.c.base.link.pk).update(revoked_at=timezone.now())
   for args in [dict(ref=ref),dict(body=b),dict(ref=b['request_id'],section='receipt')]:self.assertEqual(self.call(**args).status_code,403)
  def test_foreign_owner_and_index_tampering_rejected(self):
   r=self.call(self.body());ref=r.data['landing_id'];self.assertEqual(self.call(ref=ref,user=self.c.base.other).status_code,403);models.CommercialLanding.objects.filter(pk=ref).update(code='altered');self.assertEqual(self.call(ref=ref).status_code,503)
  def test_real_orm_audit_failure_rolls_back_all_rows(self):
   with patch.object(models.LandingEvent.objects,'create',side_effect=RuntimeError('synthetic audit unavailable')):
    with self.assertRaises(RuntimeError):self.call(self.body())
   self.assertEqual(models.CommercialLanding.objects.filter(scope=str(self.c.base.tenant.pk)).count(),0)
  def test_missing_audit_tail_never_serves_public_content(self):
   r=self.call(self.body());ref=r.data['landing_id'];models.LandingEvent.objects.filter(item_id=ref).delete();req=APIRequestFactory().get('/public/');response=api.PublicLandingView.as_view()(req,item_id=ref);self.assertEqual(response.status_code,503)
 Checks.__name__=system.replace('-','')+'NativeLanding';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
