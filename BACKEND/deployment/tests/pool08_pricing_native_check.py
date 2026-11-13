"""Native own pricing models and APIs exercised against disposable ORM databases."""
import runpy,unittest,importlib,os,sys,copy
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent))
from pool08_pricing_cases import PricingCases
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_crm_native_check.py')),run_name='pricing_native_fixture')
from django.db import connection
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.turismo.models import VerifiedCompanyLink
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 models=importlib.import_module(path+'.pricing_models')
 with connection.schema_editor() as editor:
  for model in (models.CommercialPrice,models.PriceEvent):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)
def cases(system,path):
 api=importlib.import_module(path+'.crm_api');models=importlib.import_module(path+'.pricing_models')
 class Checks(PricingCases,unittest.TestCase):
  def setUp(self):
   self.base=fixture['fixture']['AdapterTests']();self.base.setUp();env=patch.dict(os.environ,{'BACKEND_SERVICE':system});env.start();self.addCleanup(env.stop)
  def tearDown(self):self.base.tearDown()
  def data(self,r):return r.data
  def call(self,method='get',body=None,ref=None,section='list',user=None,provider=None):
   request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(provider or self.base.provider.pk),body,format='json');force_authenticate(request,user=user or self.base.user);return api.PricesView.as_view()(request,section='commands' if method=='post' else section,**({'item_id':ref} if ref else {}))
  def test_other_company_revoked_link_and_tourism(self):
   ref=self.create();self.assertEqual(self.call(ref=ref,user=self.base.other).status_code,403);VerifiedCompanyLink.objects.filter(provider=self.base.provider).update(revoked_at=__import__('django.utils.timezone',fromlist=['now']).now());self.assertEqual(self.call().status_code,403)
   with patch.dict(os.environ,{'BACKEND_SERVICE':'turismo'}):self.assertEqual(self.call().status_code,404)
  def test_delegated_staff_cannot_manage_or_apply_discount(self):
   from api.models import CustomUser,BusinessUserProfile
   from datetime import timedelta
   from django.utils import timezone
   identity=importlib.import_module(path+'.identity')
   ref=self.create();staff=CustomUser(username=__import__('uuid').uuid4().hex,role='BUSINESS_EMPLOYEE',is_active=True);CustomUser.objects.bulk_create([staff]);BusinessUserProfile.objects.create(user=staff,provider=self.base.provider,position='Equipo ofertas',is_admin=True)
   owner=identity.resolve_access(self.base.user,str(self.base.provider.pk));subject=owner.subject(str(staff.pk));owner.grant(str(staff.pk),dict(request_id=str(__import__('uuid').uuid4()),capabilities=['crm.prospect.manage','quote.prepare'],role_fingerprint=subject['role_fingerprint'],expected_revision=0,expires_at=(timezone.now()+timedelta(days=1)).isoformat(),evidence_digest='a'*64))
   self.assertEqual(self.call(user=staff).status_code,200);self.assertEqual(self.call('post',self.body(**self.values()),user=staff).status_code,403);self.assertEqual(self.call('post',self.offer(ref),user=staff).status_code,403);self.assertEqual(self.call('post',self.offer(ref,discount_bps=0),user=staff).status_code,200)
  def test_history_tampering_blocks_new_revision(self):
   ref=self.create();self.call('post',self.body('update',ref,1,title='Otra'));row=models.PriceEvent.objects.filter(item_id=ref).order_by('sequence').first();v=copy.deepcopy(row.document);v['data']['unit_price']='0.01';row.document=v;row.save();self.assertEqual(self.call(ref=ref,section='history').status_code,503);self.assertEqual(self.call('post',self.body('update',ref,2,title='Bypass')).status_code,503)
  def test_audit_failure_rolls_back(self):
   with patch.object(models.PriceEvent.objects,'create',side_effect=RuntimeError('audit unavailable')):
    with self.assertRaises(RuntimeError):self.call('post',self.body(**self.values()))
   self.assertEqual(models.CommercialPrice.objects.filter(scope=str(self.base.tenant.pk)).count(),0)
 Checks.__name__=system.replace('-','_')+'Pricing';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
