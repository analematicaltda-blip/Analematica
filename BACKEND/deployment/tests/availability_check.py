"""Capacity contracts on synthetic, isolated domain tables; no money or reservations created."""
import runpy,unittest,uuid
from pathlib import Path
from datetime import timedelta
from django.utils import timezone
fixture=runpy.run_path(str(Path(__file__).with_name('company_identity_check.py')),run_name='capacity_fixture')
from apps.turismo.models import TourismService,Reservation,AvailabilityHold,VerifiedCompanyLink
for model in (TourismService,Reservation,AvailabilityHold):fixture['fixture']['create'](model)
from apps.prestadores.mi_negocio.gestion_comercial.availability import availability,create_hold,release_hold,present
from rest_framework.exceptions import APIException
from django.test import override_settings
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_comercial.availability_views import ServiceAvailability,CapacityHoldCreate,CapacityHoldRelease

class CapacityChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['CompanyChecks']();self.case.setUp();self.case.review(apply=True)
  self.owner=fixture['F'].owner;self.other=fixture['F'].other
  self.service=TourismService.objects.create(provider=self.case.provider,name='Synthetic slot',description='test',service_type='EXPERIENCE',price='10.00',capacity=2)
  self.start=timezone.now()+timedelta(days=1);self.end=self.start+timedelta(hours=1)
 def data(self,**extra):
  value={'provider_id':str(self.case.provider.pk),'service_id':str(self.service.pk),'start_at':self.start.isoformat(),'end_at':self.end.isoformat(),'quantity':1};value.update(extra);return value
 def hold(self,**extra):return create_hold(self.owner,{**self.data(),'idempotency_key':str(uuid.uuid4()),**extra})
 def test_capacity_consumption_and_overbooking_rejection(self):
  first,_=self.hold(quantity=2);state=availability(self.owner,self.data());self.assertEqual(state['remaining_units'],0);self.assertFalse(state['can_hold'])
  with self.assertRaises(APIException):self.hold()
  self.assertFalse(Reservation.objects.filter(service=self.service).exists());self.assertFalse(present(first)['reservation_confirmed'])
 def test_half_open_adjacent_intervals_do_not_overlap(self):
  self.hold(quantity=2)
  state=availability(self.owner,self.data(start_at=self.end.isoformat(),end_at=(self.end+timedelta(hours=1)).isoformat()));self.assertEqual(state['remaining_units'],2)
 def test_peak_counts_simultaneous_units_not_sum_of_disjoint_holds(self):
  middle=self.start+timedelta(minutes=30)
  self.hold(end_at=middle.isoformat());self.hold(start_at=middle.isoformat())
  self.assertEqual(availability(self.owner,self.data())['remaining_units'],1)
 def test_expired_holds_free_capacity_but_replay_does_not_renew(self):
  hold,_=self.hold(quantity=2);AvailabilityHold.objects.filter(pk=hold.pk).update(expires_at=timezone.now()-timedelta(seconds=1))
  replay,created=self.hold(quantity=2,idempotency_key=str(hold.idempotency_key));self.assertFalse(created);self.assertEqual(present(replay)['status'],'EXPIRED')
  self.assertEqual(availability(self.owner,self.data())['remaining_units'],2)
 def test_same_request_is_idempotent_and_changed_payload_rejected(self):
  hold,_=self.hold();again,created=self.hold(idempotency_key=str(hold.idempotency_key));self.assertEqual(again.pk,hold.pk);self.assertFalse(created)
  with self.assertRaises(APIException):self.hold(quantity=2,idempotency_key=str(hold.idempotency_key))
 def test_release_is_repeat_safe_and_restores_capacity(self):
  hold,_=self.hold(quantity=2)
  for _ in (0,1):self.assertEqual(present(release_hold(self.owner,hold.pk))['status'],'RELEASED')
  self.assertEqual(availability(self.owner,self.data())['remaining_units'],2)
 def test_other_users_and_revoked_links_cannot_use_holds(self):
  hold,_=self.hold()
  with self.assertRaises(APIException):availability(self.other,self.data())
  with self.assertRaises(APIException):release_hold(self.other,hold.pk)
  VerifiedCompanyLink.objects.filter(provider=self.case.provider).update(revoked_at=timezone.now())
  with self.assertRaises(APIException):self.hold(idempotency_key=str(hold.idempotency_key))
 def test_service_cannot_be_moved_between_providers(self):
  foreign=TourismService.objects.create(provider=fixture['F'].q,name='Foreign',description='test',service_type='TOUR',price='1',capacity=2)
  with self.assertRaises(APIException):self.hold(service_id=str(foreign.pk))
 def test_legacy_reservations_require_manual_capacity_reconciliation(self):
  Reservation.objects.create(provider=self.case.provider,service=self.service,customer=fixture['F'].customer,start_date=self.start,end_date=self.end,total_price='10.00')
  state=availability(self.owner,self.data());self.assertTrue(state['requires_reconciliation']);self.assertIsNone(state['remaining_units'])
  with self.assertRaises(APIException):self.hold()
 def test_disabled_service_rejects_new_holds(self):
  self.service.availability=False;self.service.save()
  with self.assertRaises(APIException):self.hold()
 def test_invalid_intervals_quantities_and_money_fields_are_rejected(self):
  values=[{'quantity':True},{'quantity':0},{'quantity':-1},{'quantity':1.5},{'end_at':self.start.isoformat()},{'start_at':self.start.replace(tzinfo=None).isoformat()},{'total_price':'0.01'},{'start_at':(timezone.now()-timedelta(days=1)).isoformat()}]
  for extra in values:
   with self.subTest(extra=extra),self.assertRaises(APIException):self.hold(**extra)
 @override_settings(ERP_CAPACITY_HOLDS_ENABLED=True)
 def test_api_requires_auth_and_returns_no_store(self):
  factory=APIRequestFactory();request=factory.post('/capacity/',self.data(),format='json')
  self.assertIn(ServiceAvailability.as_view()(request).status_code,(401,403))
  request=factory.post('/capacity/',self.data(),format='json');force_authenticate(request,user=self.owner)
  result=ServiceAvailability.as_view()(request);self.assertEqual(result.status_code,200);self.assertEqual(result['Cache-Control'],'no-store')
 @override_settings(ERP_CAPACITY_HOLDS_ENABLED=True)
 def test_api_create_replay_and_release_without_charging(self):
  factory=APIRequestFactory();body={**self.data(),'idempotency_key':str(uuid.uuid4())}
  ids=[]
  for expected in (201,200):
   request=factory.post('/holds/',body,format='json');force_authenticate(request,user=self.owner)
   response=CapacityHoldCreate.as_view()(request);self.assertEqual(response.status_code,expected);ids.append(response.data['id']);self.assertEqual(response.data['price_state'],'UNPRICED_NO_PAYMENT')
  self.assertEqual(ids[0],ids[1])
  request=factory.post('/release/',{},format='json');force_authenticate(request,user=self.owner)
  response=CapacityHoldRelease.as_view()(request,pk=ids[0]);self.assertEqual(response.status_code,200);self.assertEqual(response.data['status'],'RELEASED')
 def test_capacity_api_is_disabled_by_default(self):
  request=APIRequestFactory().post('/capacity/',self.data(),format='json');force_authenticate(request,user=self.owner)
  self.assertEqual(ServiceAvailability.as_view()(request).status_code,503)
if __name__=='__main__':unittest.main()
