"""Real provider/customer HTTP and ORM checks using temporary schema only."""
import os,runpy,unittest
from pathlib import Path
os.environ['CHECK_SERVICE']='turismo'
runpy.run_path(str(Path(__file__).with_name('tourism_runtime_check.py')),run_name='fixture_setup')
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient,APIRequestFactory,force_authenticate
from api.models import CustomUser
from apps.turismo.models.provider_models import TourismProvider,TourismService,BusinessProfile,Reservation
from apps.turismo.api.provider_views import TourismProviderViewSet,TourismServiceViewSet,BusinessProfileViewSet,ReservationViewSet
from apps.turismo.services.financial_service import TourismFinancialService,TourismPaymentUnavailable
from apps.turismo.services.rnt_integration import RNTIntegrationService,RNTIntegrationUnavailable

created=set();visiting=set()
def create(model):
 model=model._meta.concrete_model
 if model._meta.db_table in created or model in visiting:return
 visiting.add(model)
 for field in model._meta.local_fields:
  if field.is_relation and field.remote_field and field.remote_field.model is not model:create(field.remote_field.model)
 for field in model._meta.local_many_to_many:create(field.remote_field.model)
 with connection.schema_editor() as editor:editor.create_model(model)
 created.add(model._meta.db_table);visiting.remove(model)

class ProviderChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  for model in [CustomUser,TourismProvider,TourismService,BusinessProfile,Reservation]:create(model)
  cls.factory=APIRequestFactory()
  cls.owner=CustomUser(username='synthetic-owner',role='BUSINESS_OWNER');cls.other=CustomUser(username='synthetic-other',role='BUSINESS_OWNER');cls.customer=CustomUser(username='synthetic-customer',role='TURISTA');cls.stranger=CustomUser(username='synthetic-stranger',role='TURISTA',is_staff=True)
  # This seeds users, not the wallet/company provisioning flow.
  CustomUser.objects.bulk_create([cls.owner,cls.other,cls.customer,cls.stranger])
  cls.p=TourismProvider.objects.create(owner=cls.owner,name='Synthetic provider A',provider_type='GUIDE',rnt_number='fixture-old')
  cls.q=TourismProvider.objects.create(owner=cls.other,name='Synthetic provider B',provider_type='HOTEL')
  cls.s=TourismService.objects.create(provider=cls.p,name='Synthetic service A',description='test',service_type='TOUR',price='25.00')
  cls.t=TourismService.objects.create(provider=cls.q,name='Synthetic service B',description='test',service_type='ACCOMMODATION',price='30.00')
  cls.bp=BusinessProfile.objects.create(provider=cls.q,legal_name='Synthetic legal name',tax_id='fixture-tax',business_address='test',phone='test',email='fixture@example.test',bank_account={'account':'synthetic-private-account'})
  cls.reservation=Reservation.objects.create(provider=cls.p,service=cls.s,customer=cls.customer,start_date=timezone.now()+timedelta(days=1),end_date=timezone.now()+timedelta(days=2),total_price='25.00',metadata={'internal':'synthetic-private-metadata'})
 def call(self,cls,action,user=None,method='get',pk=None,data=None):
  request=getattr(self.factory,method)('/isolated/',data=data or {},format='json')
  if user:force_authenticate(request,user=user)
  return cls.as_view({method:action})(request,**({'pk':pk} if pk is not None else {}))
 def test_01_foreign_service_and_private_business_profile_are_not_visible(self):
  self.assertEqual(self.call(TourismServiceViewSet,'retrieve',self.owner,pk=self.t.pk).status_code,404)
  self.assertEqual(self.call(BusinessProfileViewSet,'retrieve',self.owner,pk=self.bp.pk).status_code,404)
  self.assertEqual(self.call(BusinessProfileViewSet,'retrieve',self.other,pk=self.bp.pk).status_code,200)
 def test_02_staff_flag_does_not_grant_cross_business_access(self):
  for view,pk in [(TourismProviderViewSet,self.p.pk),(BusinessProfileViewSet,self.bp.pk),(ReservationViewSet,self.reservation.pk)]:self.assertEqual(self.call(view,'retrieve',self.stranger,pk=pk).status_code,404)
 def test_03_owner_updates_own_service_and_cannot_transfer_it(self):
  r=self.call(TourismServiceViewSet,'partial_update',self.owner,'patch',self.s.pk,{'description':'Synthetic updated'});self.assertEqual(r.status_code,200,r.data)
  self.assertEqual(self.call(TourismServiceViewSet,'partial_update',self.owner,'patch',self.s.pk,{'provider':str(self.q.pk)}).status_code,400)
  self.assertEqual(self.call(TourismServiceViewSet,'partial_update',self.owner,'patch',self.s.pk,{'price':'-1.00'}).status_code,400)
 def test_04_foreign_provider_rejected_on_service_create(self):
  r=self.call(TourismServiceViewSet,'create',self.owner,'post',data={'provider':str(self.q.pk),'name':'Injected','description':'test','service_type':'TOUR','price':'1.00'});self.assertEqual(r.status_code,400);self.assertFalse(TourismService.objects.filter(name='Injected').exists())
 def test_05_local_provider_declaration_cannot_forge_rnt_or_score(self):
  r=self.call(TourismProviderViewSet,'create',self.owner,'post',data={'name':'Synthetic new provider','provider_type':'GUIDE','owner':self.other.pk,'rnt_number':'12345','rnt_validated':True,'puntuacion_total':999});self.assertEqual(r.status_code,201,r.data)
  p=TourismProvider.objects.get(name='Synthetic new provider');self.assertEqual(p.owner_id,self.owner.pk);self.assertFalse(p.rnt_validated);self.assertEqual(p.puntuacion_total,0);self.assertIsNone(p.rnt_last_sync)
  self.assertEqual(self.call(TourismProviderViewSet,'create',self.customer,'post',data={'name':'Not allowed','provider_type':'GUIDE'}).status_code,403)
 def test_06_changing_declared_rnt_invalidates_prior_verification(self):
  self.p.rnt_validated=True;self.p.rnt_last_sync=timezone.now();self.p.save(update_fields=['rnt_validated','rnt_last_sync'])
  r=self.call(TourismProviderViewSet,'partial_update',self.owner,'patch',self.p.pk,{'rnt_number':'fixture-new','rnt_validated':True});self.assertEqual(r.status_code,200,r.data);self.p.refresh_from_db();self.assertFalse(self.p.rnt_validated);self.assertIsNone(self.p.rnt_last_sync)
 def test_07_rnt_sync_checks_scope_and_never_fabricates_success(self):
  self.assertEqual(self.call(TourismProviderViewSet,'sync_rnt',self.owner,'post',self.q.pk).status_code,404)
  self.assertEqual(self.call(TourismProviderViewSet,'sync_rnt',self.owner,'post',self.p.pk).status_code,503)
  self.p.refresh_from_db();self.assertFalse(self.p.rnt_validated)
 def test_08_reservation_read_is_scoped_and_metadata_is_private(self):
  for user in [self.customer,self.owner]:
   r=self.call(ReservationViewSet,'retrieve',user,pk=self.reservation.pk);self.assertEqual(r.status_code,200);self.assertNotIn('metadata',r.data)
  self.assertEqual(self.call(ReservationViewSet,'retrieve',self.other,pk=self.reservation.pk).status_code,404)
 def test_09_payment_action_checks_scope_then_refuses_execution(self):
  self.assertEqual(self.call(ReservationViewSet,'process_payment',self.other,'post',self.reservation.pk).status_code,404)
  self.assertEqual(self.call(ReservationViewSet,'process_payment',self.customer,'post',self.reservation.pk).status_code,503)
  self.reservation.refresh_from_db();self.assertEqual(self.reservation.status,'PENDING')
 def test_10_service_boundaries_do_not_issue_sql_or_wallet_events(self):
  def refuse(*args,**kwargs):raise AssertionError('Disabled integration accessed database')
  from unittest.mock import patch
  with connection.execute_wrapper(refuse),patch('apps.core_erp.event_bus.EventBus.emit',side_effect=AssertionError('No financial events allowed')):
   for call in [lambda:TourismFinancialService.process_reservation_payment(self.reservation.pk),lambda:TourismFinancialService.register_transaction(self.p,1,self.customer),lambda:TourismFinancialService.get_provider_balance(self.p.pk)]:
    with self.assertRaises(TourismPaymentUnavailable):call()
   for call in [lambda:RNTIntegrationService.validate_rnt('12345'),lambda:RNTIntegrationService.sync_provider(self.p.pk),lambda:RNTIntegrationService.login_via_rnt('12345',None)]:
    with self.assertRaises(RNTIntegrationUnavailable):call()
 def test_11_full_routes_reject_reservation_tampering_and_number_only_login(self):
  client=APIClient(HTTP_HOST='localhost');root='/api/v1/turismo/v1/'
  r=client.post(root+'tourism-providers/login-rnt/',{'rnt_number':'12345'},format='json');self.assertEqual(r.status_code,503,r.content)
  client.force_authenticate(self.customer)
  for method,path in [('post','tourism-reservations/'),('patch','tourism-reservations/'+str(self.reservation.pk)+'/'),('delete','tourism-reservations/'+str(self.reservation.pk)+'/')]:
   response=getattr(client,method)(root+path,{'status':'CONFIRMED','total_price':'0.01','customer':self.other.pk},format='json');self.assertEqual(response.status_code,405,response.content)
  self.reservation.refresh_from_db();self.assertEqual(self.reservation.total_price,25);self.assertEqual(self.reservation.customer_id,self.customer.pk)
 def test_12_me_serialization_keeps_private_profile_scoped(self):
  r=self.call(TourismProviderViewSet,'me',self.other);self.assertEqual(r.status_code,200,r.data);self.assertEqual(r.data['business_profile']['tax_id'],'fixture-tax')

if __name__=='__main__':unittest.main()
