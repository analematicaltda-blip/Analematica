import runpy,unittest,importlib,os,sys,uuid,copy
from pathlib import Path
from unittest.mock import patch
from datetime import datetime,timezone,timedelta
sys.path.insert(0,str(Path(__file__).parent))
from pool08_quotation_cases import QuotationCases
fixture=runpy.run_path(str(Path(__file__).with_name('pool08_pricing_native_check.py')),run_name='quotation_native_fixture')
from django.db import connection
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.turismo.models import TourismService,Reservation,AvailabilityHold,VerifiedCompanyLink
for path in ('apps.prestadores.mi_negocio.gestion_comercial.pool08','apps.admin_plataforma.gestion_comercial.pool08'):
 models=importlib.import_module(path+'.quotation_models')
 with connection.schema_editor() as editor:
  for model in (models.CommercialQuotation,models.QuotationEvent,models.QuotationAsset,TourismService,Reservation,AvailabilityHold):
   if model._meta.db_table not in connection.introspection.table_names():editor.create_model(model)
def cases(system,path):
 api=importlib.import_module(path+'.crm_api');models=importlib.import_module(path+'.quotation_models')
 class Checks(QuotationCases,unittest.TestCase):
  domain_path=path
  def setUp(self):
   self.base=fixture['fixture']['fixture']['AdapterTests']();self.base.setUp();env=patch.dict(os.environ,{'BACKEND_SERVICE':system,'COMMERCIAL_QUOTE_LINK_KEY':'synthetic-quotation-test-key-32-chars-only'});env.start();self.addCleanup(env.stop)
   request=APIRequestFactory().post('/crm/?provider_id='+str(self.base.provider.pk),dict(request_id=str(uuid.uuid4()),operation='create',contact_id=None,expected_revision=0,data={'name':'Contacto de cotización','email':uuid.uuid4().hex+'@example.test','origin':'MANUAL','responsible_ref':str(self.base.user.pk)}),format='json');force_authenticate(request,user=self.base.user);response=api.CRMView.as_view()(request,section='commands');self.assertEqual(response.status_code,200,response.data);self.contact=response.data['contact_id']
  def tearDown(self):self.base.tearDown()
  def data(self,r):return r.data
  def price_call(self,body):
   request=APIRequestFactory().post('/fixture/?provider_id='+str(self.base.provider.pk),body,format='json');force_authenticate(request,user=self.base.user);return api.PricesView.as_view()(request,section='commands')
  def call(self,method='get',body=None,ref=None,section='list',user=None):
   request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.base.provider.pk),body,format='json');force_authenticate(request,user=user or self.base.user);return api.QuotationsView.as_view()(request,section='commands' if method=='post' else section,**({'quotation_id':ref} if ref else {}))
  def upload(self,ref,raw,mime):
   request=APIRequestFactory().post('/media/?provider_id='+str(self.base.provider.pk),raw,content_type=mime);force_authenticate(request,user=self.base.user);return api.QuoteMediaView.as_view()(request,asset_id=ref)
  def public(self,ref,link,body=None,asset=None):
   request=getattr(APIRequestFactory(),'post' if body else 'get')('/public/',body,format='json',HTTP_X_QUOTE_TOKEN=link['link_token']);return api.PublicQuoteView.as_view()(request,quotation_id=ref,link_id=link['link_id'],**({'asset_id':asset} if asset else {}))
  def test_other_company_revocation_and_tourism(self):
   ref=self.create();self.issue(ref);link=self.link(ref);self.assertEqual(self.call(ref=ref,user=self.base.other).status_code,403);VerifiedCompanyLink.objects.filter(provider=self.base.provider).update(revoked_at=datetime.now(timezone.utc));self.assertEqual(self.public(ref,link).status_code,403)
   with patch.dict(os.environ,{'BACKEND_SERVICE':'turismo'}):self.assertEqual(self.call().status_code,404)
  def test_native_capacity_source_and_changed_hold_blocks_acceptance(self):
   service=TourismService.objects.create(provider=self.base.provider,name='Cupo sintético',description='test',service_type='EXPERIENCE',price='10.00',capacity=2)
   price=self.price();self.policy(price,'REQUIRED',str(service.pk));start=datetime.now(timezone.utc)+timedelta(days=1);end=start+timedelta(hours=1);windows=[dict(item_id=price,start_at=start.isoformat(),end_at=end.isoformat())];ref=self.create(price,policy=False,service_windows=windows);self.issue(ref);link=self.link(ref)
   self.assertEqual(AvailabilityHold.objects.filter(service=service).count(),0)
   AvailabilityHold.objects.create(provider=self.base.provider,service=service,requested_by=self.base.user,idempotency_key=uuid.uuid4(),request_digest='a'*64,start_at=start,end_at=end,quantity=2,expires_at=datetime.now(timezone.utc)+timedelta(hours=1))
   self.assertEqual(self.public(ref,link,self.acceptance(ref)).status_code,409);self.assertEqual(self.data(self.call(ref=ref))['status'],'ISSUED')
  def test_audit_failure_rolls_back(self):
   price=self.price();self.policy(price)
   with patch.object(models.QuotationEvent.objects,'create',side_effect=RuntimeError('audit unavailable')):
    with self.assertRaises(RuntimeError):self.call('post',self.body(**self.values(price)))
   self.assertEqual(models.CommercialQuotation.objects.filter(scope=str(self.base.tenant.pk)).exclude(status='CAPACITY_POLICY').count(),0)
 Checks.__name__=system.replace('-','_')+'Quotations';return Checks
ERP=cases('erp-tur','apps.prestadores.mi_negocio.gestion_comercial.pool08');Ana=cases('analematica','apps.admin_plataforma.gestion_comercial.pool08')
if __name__=='__main__':unittest.main()
