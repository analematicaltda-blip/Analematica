"""Durable reviewed observations, exact factor versions and activity uniqueness."""
import copy,runpy,unittest
from pathlib import Path
from datetime import timedelta
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_adapter_check.py')),run_name='environmental_records_fixture')
from django.utils import timezone
from apps.prestadores.mi_negocio.gestion_contable.contabilidad import environmental_records as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.exceptions import PermissionDenied

class EnvironmentalRecordChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['AdapterTests']();self.case.setUp();self.owner=self.case.user;self.company=self.case.tenant;self.provider=self.case.provider;self.day=timezone.localdate().isoformat()
  self.factor={'id':'fixture-diesel','version':'synthetic-v1','unit':'vehicle_km','kg_co2e_per_unit':'0.123456','valid_from':self.day[:4]+'-01-01','valid_until':self.day[:4]+'-12-31','source_digest':'a'*64,'geography':'CO','boundary':'direct_combustion'}
  self.activity={'id':'route-1','date':self.day,'quantity':'100','unit':'vehicle_km','factor_id':'fixture-diesel','passengers':4}
  self.args={'actor':self.owner,'provider_id':self.provider.pk,'activities':[self.activity],'factors':[self.factor],'evidence_digest':'b'*64,'confirmed':True}
 def review(self,**extra):return engine.review_measurement(**{**self.args,**extra})
 def record(self,review,**extra):return engine.record_measurement(**{'actor':self.owner,'provider_id':self.provider.pk,'review_id':review['review_id'],'confirmed':True,**extra})
 def state(self,review):return engine.measurement_state(actor=self.owner,provider_id=self.provider.pk,review_id=review['review_id'])
 def test_two_confirmations_and_no_ledger_payment_or_liability(self):
  before=JournalEntry.plain_objects.count()
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.record(r,confirmed=False)
  recorded=self.record(r);self.assertEqual(before,JournalEntry.plain_objects.count());self.assertEqual(self.state(r)['applied']['observation_id'],recorded['observation_id'])
  for key in ['ledger_written','money_transferred','liability_recognized','carbon_credit_issued','independently_verified']:self.assertIs(recorded[key],False)
 def test_retry_recovers_identical_observation_no_duplicate_events(self):
  r=self.review();self.assertEqual(r,self.review());first=self.record(r);count=OutboxEvent.objects.count();again=self.record(r);self.assertEqual(first['observation_id'],again['observation_id']);self.assertTrue(again['replayed']);self.assertEqual(count,OutboxEvent.objects.count())
 def test_status_does_not_restore_confirmations(self):
  r=self.review();s=self.state(r);self.assertIsNone(s['applied']);self.assertFalse(s['confirmations_restored']);self.assertTrue(s['reviewed_by_current_owner']);self.assertEqual(s['preview']['assessment']['kg_co2e'],'12.345600')
 def test_same_activity_cannot_be_recorded_by_another_review(self):
  self.record(self.review());other=self.review(evidence_digest='c'*64)
  with self.assertRaises(AccountingError):self.record(other)
  self.assertIsNone(self.state(other)['applied'])
 def test_changed_activity_quantity_cannot_bypass_uniqueness(self):
  self.record(self.review());r=self.review(activities=[{**self.activity,'quantity':'101'}])
  with self.assertRaises(AccountingError):self.record(r)
 def test_one_factor_version_cannot_change_value_or_source(self):
  self.record(self.review())
  for change in [{'kg_co2e_per_unit':'0.2'},{'source_digest':'c'*64},{'geography':'MX'}]:
   r=self.review(activities=[{**self.activity,'id':'route-2'}],factors=[{**self.factor,**change}])
   with self.assertRaises(AccountingError):self.record(r)
 def test_new_factor_version_preserves_previous_evidence(self):
  old=self.review();self.record(old);r=self.review(activities=[{**self.activity,'id':'route-2'}],factors=[{**self.factor,'version':'synthetic-v2','kg_co2e_per_unit':'0.2'}]);self.record(r)
  self.assertEqual(self.state(old)['preview']['assessment']['kg_co2e'],'12.345600');self.assertEqual(self.state(r)['preview']['assessment']['kg_co2e'],'20.000000')
 def test_partial_claims_rollback_if_later_activity_conflicts(self):
  self.record(self.review());before=OutboxEvent.objects.count();r=self.review(activities=[{**self.activity,'id':'a-new'},self.activity],factors=[{**self.factor,'version':'synthetic-v2'}]);count=OutboxEvent.objects.count()
  with self.assertRaises(AccountingError):self.record(r)
  self.assertEqual(count,OutboxEvent.objects.count());self.assertEqual(count,before+1)
 def test_failed_timestamp_seal_rolls_back_all_claims(self):
  from django.db.models.query import QuerySet
  r=self.review();count=OutboxEvent.objects.count()
  with patch.object(QuerySet,'update',side_effect=AccountingError('synthetic failure')):
   with self.assertRaises(AccountingError):self.record(r)
  self.assertEqual(count,OutboxEvent.objects.count());self.assertIsNone(self.state(r)['applied']);self.assertFalse(self.record(r)['replayed'])
 def test_review_tampering_rejected(self):
  r=self.review();row=OutboxEvent.objects.get(pk=r['review_id']);body=copy.deepcopy(row.payload);body['review']['assessment']['kg_co2e']='0';OutboxEvent.objects.filter(pk=row.pk).update(payload=body)
  with self.assertRaises(AccountingError):self.record(r)
 def test_factor_claim_tampering_rejected_on_recovery(self):
  r=self.review();self.record(r);row=OutboxEvent.objects.filter(event_type=engine.FACTOR,payload__company_id=str(self.company.pk)).first();body=copy.deepcopy(row.payload);body['content']['kg_co2e_per_unit']='0';OutboxEvent.objects.filter(pk=row.pk).update(payload=body)
  with self.assertRaises(AccountingError):self.state(r)
 def test_activity_claim_missing_rejected_on_recovery(self):
  r=self.review();self.record(r);OutboxEvent.objects.filter(event_type=engine.ACTIVITY,payload__company_id=str(self.company.pk)).delete()
  with self.assertRaises(AccountingError):self.state(r)
 def test_known_timestamp_tampering_rejected(self):
  r=self.review();record=self.record(r);OutboxEvent.objects.filter(pk=record['observation_id']).update(created_at=timezone.now()+timedelta(days=1))
  with self.assertRaises(AccountingError):self.state(r)
 def test_other_owner_and_company_rejected(self):
  r=self.review();other=fixture['AdapterTests']();other.setUp()
  with self.assertRaises(PermissionDenied):self.record(r,actor=self.case.other)
  with self.assertRaises(AccountingError):engine.measurement_state(actor=other.user,provider_id=other.provider.pk,review_id=r['review_id'])
 def test_future_activity_estimate_cannot_be_recorded_as_observed(self):
  future=(timezone.localdate()+timedelta(days=1)).isoformat()
  with self.assertRaises(AccountingError):self.review(activities=[{**self.activity,'date':future}])
 def test_real_api_review_record_status_and_private_response(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  def call(action,body,method='post'):
   if method=='get':body={'provider_id':str(self.provider.pk),**body}
   request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.provider.pk),body,format='json');force_authenticate(request,user=self.owner);return PlanCuentaViewSet.as_view({method:action})(request)
  payload={k:v for k,v in self.args.items() if k not in {'actor','provider_id'}};r=call('review_environmental',payload);self.assertEqual(r.status_code,200,r.data);recorded=call('record_environmental',{'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(recorded.status_code,200,recorded.data)
  state=call('environmental_state',{'review_id':r.data['review_id']},'get');self.assertEqual(state.status_code,200,state.data);self.assertEqual(state.data['applied']['observation_id'],recorded.data['observation_id']);self.assertIn('no-store',state['Cache-Control']);self.assertFalse(state.data['confirmations_restored'])
if __name__=='__main__':unittest.main()
