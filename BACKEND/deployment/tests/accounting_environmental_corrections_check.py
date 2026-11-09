"""Append-only corrections, stale reviews and isolation in disposable ORM/API."""
import copy,runpy,unittest
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_environmental_records_check.py')),run_name='environmental_corrections_fixture')
from apps.prestadores.mi_negocio.gestion_contable.contabilidad import environmental_corrections as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.exceptions import PermissionDenied

class EnvironmentalCorrectionChecks(unittest.TestCase):
 def setUp(self):
  self.case=fixture['EnvironmentalRecordChecks']();self.case.setUp();self.original_review=self.case.review();self.original_record=self.case.record(self.original_review)
  self.company=self.case.company;self.owner=self.case.owner;self.provider=self.case.provider;self.observation=self.original_record['observation_id']
  self.args={'actor':self.owner,'provider_id':self.provider.pk,'observation_id':self.observation,'expected_revision':0,'activities':[{**self.case.activity,'quantity':'200'}],'factors':[self.case.factor],'evidence_digest':'c'*64,'reason_code':'QUANTITY_ERROR','confirmed':True}
 def review(self,**changes):return engine.review_correction(**{**self.args,**changes})
 def record(self,review,**changes):return engine.record_correction(**{'actor':self.owner,'provider_id':self.provider.pk,'observation_id':self.observation,'review_id':review['review_id'],'confirmed':True,**changes})
 def state(self):return engine.correction_state(actor=self.owner,provider_id=self.provider.pk,observation_id=self.observation)
 def test_effective_estimate_replaces_original_without_new_activity_or_ledger(self):
  before=JournalEntry.plain_objects.count();original=copy.deepcopy(OutboxEvent.objects.get(pk=self.observation).payload);claims=OutboxEvent.objects.filter(event_type=engine.records.ACTIVITY).count()
  review=self.review();record=self.record(review);state=self.state()
  self.assertEqual(state['original_assessment']['kg_co2e'],'12.345600');self.assertEqual(state['effective_assessment']['kg_co2e'],'24.691200');self.assertEqual(state['revision'],1);self.assertTrue(state['effective_total_replaces_original']);self.assertFalse(state['confirmations_restored'])
  self.assertEqual(original,OutboxEvent.objects.get(pk=self.observation).payload);self.assertEqual(claims,OutboxEvent.objects.filter(event_type=engine.records.ACTIVITY).count());self.assertEqual(before,JournalEntry.plain_objects.count())
  for k in ['ledger_written','money_transferred','liability_recognized','carbon_credit_issued','independently_verified','esg_certified']:self.assertIs(record[k],False)
 def test_two_confirmations_and_retries_do_not_duplicate(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.record(r,confirmed=False)
  a=self.record(r);count=OutboxEvent.objects.count();b=self.record(r);self.assertTrue(b['replayed']);self.assertEqual(a['correction_id'],b['correction_id']);self.assertEqual(count,OutboxEvent.objects.count())
 def test_competing_reviews_only_current_head_can_record(self):
  a=self.review();b=self.review(activities=[{**self.case.activity,'quantity':'300'}]);self.record(a)
  with self.assertRaises(AccountingError):self.record(b)
  with self.assertRaises(AccountingError):self.review()
  self.assertEqual(self.state()['revision'],1)
 def test_second_revision_preserves_history_and_old_result_is_recoverable(self):
  first=self.review();a=self.record(first);second=self.review(expected_revision=1,activities=[{**self.case.activity,'quantity':'300'}]);b=self.record(second);state=self.state()
  self.assertEqual(state['revision'],2);self.assertEqual(state['effective_assessment']['kg_co2e'],'37.036800');self.assertEqual(state['history'][1]['previous_digest'],a['correction_digest']);self.assertEqual(b['correction_digest'],state['head_digest']);self.assertTrue(self.record(first)['replayed']);self.assertEqual(self.state(),state)
 def test_changed_factor_requires_new_version(self):
  r=self.review(factors=[{**self.case.factor,'kg_co2e_per_unit':'0.2'}])
  with self.assertRaises(AccountingError):self.record(r)
  self.assertEqual(self.state()['revision'],0)
  r=self.review(factors=[{**self.case.factor,'version':'synthetic-v2','kg_co2e_per_unit':'0.2'}]);self.record(r);self.assertEqual(self.state()['effective_assessment']['kg_co2e'],'40.000000');self.assertEqual(self.state()['original_assessment']['kg_co2e'],'12.345600')
 def test_activity_identity_date_and_unit_cannot_be_reclaimed(self):
  for change in [{'id':'another-route'},{'date':self.case.day[:8]+'01'},{'unit':'litre_fuel'}]:
   if change.get('date')==self.case.day:continue
   with self.assertRaises(AccountingError):self.review(activities=[{**self.case.activity,**change}])
 def test_noop_and_invalid_reason_or_revision_denied(self):
  for change in [{'activities':[self.case.activity]},{'reason_code':'CERTIFIED_OFFSET'},{'expected_revision':True},{'expected_revision':-1},{'evidence_digest':'invalid'}]:
   with self.assertRaises(AccountingError):self.review(**change)
 def test_review_digest_and_chain_tampering_denied(self):
  r=self.review();row=OutboxEvent.objects.get(pk=r['review_id']);payload=copy.deepcopy(row.payload);row.payload['review']['assessment']['kg_co2e']='0';row.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.record(r)
  row.payload=payload;row.save(update_fields=['payload']);result=self.record(r);record=OutboxEvent.objects.get(pk=result['correction_id']);record.payload['previous_digest']='f'*64;record.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.state()
 def test_missing_intermediate_correction_rejects_later_chain(self):
  a=self.record(self.review());self.record(self.review(expected_revision=1,activities=[{**self.case.activity,'quantity':'300'}]));OutboxEvent.objects.filter(pk=a['correction_id']).delete()
  with self.assertRaises(AccountingError):self.state()
 def test_original_and_corrected_factor_claims_are_verified(self):
  r=self.review(factors=[{**self.case.factor,'version':'synthetic-v2','kg_co2e_per_unit':'0.2'}]);self.record(r)
  factor=OutboxEvent.objects.filter(event_type=engine.records.FACTOR,payload__key='fixture-diesel:synthetic-v2',payload__company_id=str(self.company.pk)).get();factor.payload['content']['kg_co2e_per_unit']='0.3';factor.save(update_fields=['payload'])
  with self.assertRaises(AccountingError):self.state()
 def test_failed_seal_rolls_back_new_factor_and_correction(self):
  r=self.review(factors=[{**self.case.factor,'version':'synthetic-v2'}]);count=OutboxEvent.objects.count()
  from django.db.models.query import QuerySet
  with patch.object(QuerySet,'update',side_effect=AccountingError('Synthetic storage failure')):
   with self.assertRaises(AccountingError):self.record(r)
  self.assertEqual(OutboxEvent.objects.count(),count);self.assertEqual(self.state()['revision'],0);self.assertFalse(self.record(r)['replayed'])
 def test_foreign_owner_and_foreign_observation_denied(self):
  r=self.review()
  with self.assertRaises(PermissionDenied):self.record(r,actor=self.case.case.other)
  other=fixture['EnvironmentalRecordChecks']();other.setUp()
  with self.assertRaises(AccountingError):engine.correction_state(actor=other.owner,provider_id=other.provider.pk,observation_id=self.observation)
 def test_revoked_binding_and_agent_denied(self):
  r=self.review()
  from django.contrib.auth import get_user_model
  get_user_model().objects.filter(pk=self.owner.pk).update(is_agent=True)
  with self.assertRaises(PermissionDenied):self.record(r)
  get_user_model().objects.filter(pk=self.owner.pk).update(is_agent=False)
  from apps.turismo.models import VerifiedCompanyLink
  VerifiedCompanyLink.objects.filter(provider=self.provider).update(revoked_at=engine.timezone.now())
  with self.assertRaises(PermissionDenied):self.state()
 def test_original_state_exposes_effective_revision_without_restoring_approvals(self):
  self.record(self.review());state=self.case.state(self.original_review);self.assertEqual(state['preview']['assessment']['kg_co2e'],'12.345600');self.assertEqual(state['corrections']['effective_assessment']['kg_co2e'],'24.691200');self.assertFalse(state['confirmations_restored'])
 def test_real_http_review_record_history_private(self):
  from rest_framework.test import APIRequestFactory,force_authenticate
  from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
  def call(action,body,method='post'):
   if method=='get':body={'provider_id':str(self.provider.pk),**body}
   req=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.provider.pk),body,format='json');force_authenticate(req,user=self.owner);return PlanCuentaViewSet.as_view({method:action})(req)
  args={k:v for k,v in self.args.items() if k not in {'actor','provider_id'}};r=call('review_environmental_correction',args);self.assertEqual(r.status_code,200,r.data)
  a=call('record_environmental_correction',{'observation_id':self.observation,'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(a.status_code,200,a.data)
  state=call('environmental_correction_state',{'observation_id':self.observation},'get');self.assertEqual(state.status_code,200,state.data);self.assertEqual(state.data['revision'],1);self.assertIn('no-store',state['Cache-Control'])
if __name__=='__main__':unittest.main()
