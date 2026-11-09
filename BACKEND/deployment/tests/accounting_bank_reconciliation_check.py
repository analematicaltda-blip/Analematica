"""Actual reviewed bank matching/release metadata; no ledger writes or raw ID storage."""
import runpy,unittest,uuid,hashlib
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_statement_check.py')),run_name='reconciliation_fixture')
from apps.core_erp.accounting import bank_reconciliation as engine
from apps.core_erp.accounting import ratios
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry,AccountingEventReceipt
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from rest_framework.test import APIRequestFactory,force_authenticate
from apps.prestadores.mi_negocio.gestion_contable.contabilidad.views import PlanCuentaViewSet
class BankReconciliationTests(unittest.TestCase):
 def setUp(self):
  self.bank=fixture['BankComparisonTests']();self.bank.setUp();self.case=self.bank.case
  self.args={'actor':self.case.user,'account_id':str(self.case.a.pk),'csv_text':self.bank.csv,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True}
 def review(self,**extra):return engine.review_reconciliation(self.case.tenant.pk,**{**self.args,**extra})
 def confirm(self,review,**extra):return engine.confirm_reconciliation(self.case.tenant.pk,**{'actor':self.case.user,'statement_id':review['statement_id'],'review_id':review['review_id'],'confirmed':True,**extra})
 def state(self):return engine.reconciliation_state(self.case.tenant.pk,actor=self.case.user,account_id=str(self.case.a.pk),source_digest=hashlib.sha256(self.bank.csv.encode()).hexdigest())
 def release_review(self,result,**extra):return engine.review_release(self.case.tenant.pk,**{'actor':self.case.user,'reconciliation_id':result['reconciliation_id'],'reason_code':'WRONG_MATCH','evidence_digest':'b'*64,'confirmed':True,**extra})
 def release(self,review,**extra):return engine.confirm_release(self.case.tenant.pk,**{'actor':self.case.user,'review_id':review['review_id'],'confirmed':True,**extra})
 def counts(self):return (JournalEntry.plain_objects.count(),LedgerEntry.plain_objects.count(),AccountingEventReceipt.objects.count())
 def test_first_review_persists_without_confirmation_or_raw_identifiers(self):
  before=self.counts();review=self.review();self.assertFalse(review['ledger_written']);self.assertFalse(OutboxEvent.objects.filter(event_type=engine.APPLIED,payload__company_id=str(self.case.tenant.pk)).exists());self.assertNotIn('private-reference-001',str(OutboxEvent.objects.filter(event_type=engine.REVIEW,payload__company_id=str(self.case.tenant.pk)).first().payload));self.assertEqual(self.counts(),before)
 def test_two_confirmations_and_unique_replay(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  review=self.review()
  with self.assertRaises(AccountingError):self.confirm(review,confirmed=False)
  before=self.counts();result=self.confirm(review);again=self.confirm(review);self.assertTrue(result['reconciliation_confirmed']);self.assertFalse(result['replayed']);self.assertTrue(again['replayed']);self.assertEqual(again['reconciliation_id'],result['reconciliation_id']);self.assertEqual(self.counts(),before);self.assertFalse(result['bank_verified']);self.assertFalse(result['money_transferred'])
 def test_changing_reference_cannot_reconcile_one_line_twice(self):
  self.confirm(self.review())
  with self.assertRaises(AccountingError):self.review(csv_text=self.bank.csv.replace('private-reference-001','different-reference'))
 def test_same_reference_cannot_claim_another_line_with_changed_amount(self):
  self.confirm(self.review());LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=self.bank.entry.date,description='Another receipt',lines_data=[{'account':self.case.a,'debit':'11.00'},{'account':self.case.b,'credit':'11.00'}],actor=self.case.user,idempotency_key='another-amount')
  with self.assertRaises(AccountingError):self.review(csv_text=self.bank.csv.replace('10.00','11.00'))
 def test_pending_competing_statements_cannot_both_confirm(self):
  one=self.review();two=self.review(csv_text=self.bank.csv.replace('private-reference-001','different-reference'));self.confirm(one)
  with self.assertRaises(AccountingError):self.confirm(two)
 def test_ambiguous_and_unmatched_batches_do_not_create_review(self):
  with self.assertRaises(AccountingError):self.review(csv_text=self.bank.csv.replace('10.00','11.00'))
  self.case.post(idempotency_key='ambiguous-ten')
  with self.assertRaises(AccountingError):self.review()
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.REVIEW,payload__company_id=str(self.case.tenant.pk)).exists())
 def test_current_revision_and_same_reviewer_required(self):
  one=self.review();self.review(expected_revision=1,evidence_digest='c'*64)
  with self.assertRaises(AccountingError):self.confirm(one)
 def test_cash_policy_changed_after_review_blocks_confirmation(self):
  review=self.review();self.case.configure_ratio(ratios.describe(ratios.latest(self.case.tenant.pk))['mapping'],expected_revision=1)
  with self.assertRaises(AccountingError):self.confirm(review)
 def test_reversed_source_before_confirmation_blocks_match(self):
  review=self.review();LedgerEngine.reverse_entry(self.bank.entry.pk,'Synthetic correction',tenant_id=self.case.tenant.pk,actor=self.case.user)
  with self.assertRaises(AccountingError):self.confirm(review)
 def test_reversal_after_confirmation_is_not_reported_as_current_valid_match(self):
  review=self.review();self.confirm(review);LedgerEngine.reverse_entry(self.bank.entry.pk,'Synthetic later correction',tenant_id=self.case.tenant.pk,actor=self.case.user)
  state=self.state();self.assertTrue(state['applied']['requires_review']);self.assertFalse(state['applied']['reconciliation_confirmed']);self.assertTrue(state['applied']['historically_confirmed'])
 def test_origin_failure_rolls_back_all_claims(self):
  review=self.review();original=OutboxEvent.objects.create
  def create(**kwargs):
   if kwargs.get('event_type')==engine.APPLIED:raise RuntimeError('Proof failed')
   return original(**kwargs)
  with patch.object(OutboxEvent.objects,'create',side_effect=create):
   with self.assertRaises(RuntimeError):self.confirm(review)
  self.assertFalse(OutboxEvent.objects.filter(event_type=engine.CLAIM,payload__company_id=str(self.case.tenant.pk)).exists());self.assertFalse(OutboxEvent.objects.filter(event_type=engine.APPLIED,payload__company_id=str(self.case.tenant.pk)).exists())
 def test_corrupt_claim_cannot_be_replayed_as_valid(self):
  review=self.review();self.confirm(review);claim=OutboxEvent.objects.filter(event_type=engine.CLAIM,payload__company_id=str(self.case.tenant.pk)).first();payload=claim.payload;payload['ledger_line_id']=str(uuid.uuid4());OutboxEvent.objects.filter(pk=claim.pk).update(payload=payload)
  with self.assertRaises(AccountingError):self.confirm(review)
 def test_release_requires_two_confirmations_preserves_history_and_replays(self):
  result=self.confirm(self.review());before=self.counts()
  with self.assertRaises(AccountingError):self.release_review(result,confirmed=False)
  review=self.release_review(result)
  with self.assertRaises(AccountingError):self.release(review,confirmed=False)
  released=self.release(review);self.assertTrue(released['released']);self.assertFalse(released['reconciliation_confirmed']);self.assertTrue(self.release(review)['replayed']);self.assertTrue(OutboxEvent.objects.filter(pk=result['reconciliation_id']).exists());self.assertTrue(OutboxEvent.objects.filter(event_type=engine.CLAIM,payload__company_id=str(self.case.tenant.pk)).exists());self.assertEqual(self.counts(),before)
 def test_release_allows_new_review_and_match_without_deleting_old_evidence(self):
  original=self.confirm(self.review());self.release(self.release_review(original));new_review=self.review(expected_revision=1);new=self.confirm(new_review);self.assertNotEqual(original['reconciliation_id'],new['reconciliation_id']);self.assertTrue(new['reconciliation_confirmed']);self.assertEqual(OutboxEvent.objects.filter(event_type=engine.APPLIED,payload__company_id=str(self.case.tenant.pk)).count(),2)
 def test_released_claim_allows_a_different_statement_to_use_the_line(self):
  result=self.confirm(self.review());self.release(self.release_review(result));second=self.confirm(self.review(csv_text=self.bank.csv.replace('private-reference-001','different-reference')));self.assertTrue(second['reconciliation_confirmed'])
 def test_corrupt_release_does_not_silently_free_claims(self):
  result=self.confirm(self.review());self.release(self.release_review(result));released=OutboxEvent.objects.filter(event_type=engine.RELEASED,payload__company_id=str(self.case.tenant.pk)).first();p=released.payload;p['review_digest']='c'*64;OutboxEvent.objects.filter(pk=released.pk).update(payload=p)
  with self.assertRaises(AccountingError):self.review(expected_revision=1)
 def test_recovery_does_not_restore_confirmation_and_exposes_only_hash_reference(self):
  review=self.review();state=self.state();self.assertEqual(state['review_id'],review['review_id']);self.assertFalse(state['confirmations_restored']);self.assertNotIn('private-reference-001',str(state));self.assertTrue(state['read_only'])
 def test_real_scoped_api_and_private_response(self):
  def call(action,data,method='post'):
   if method=='get':data={'provider_id':str(self.case.provider.pk),**data}
   request=getattr(APIRequestFactory(),method)('/fixture/?provider_id='+str(self.case.provider.pk),data,format='json');force_authenticate(request,user=self.case.user);return PlanCuentaViewSet.as_view({method:action})(request)
  review=call('review_bank_reconciliation',{k:v for k,v in self.args.items() if k!='actor'});self.assertEqual(review.status_code,200,review.data)
  confirmed=call('confirm_bank_reconciliation',{'statement_id':review.data['statement_id'],'review_id':review.data['review_id'],'confirmed':True});self.assertEqual(confirmed.status_code,200,confirmed.data);self.assertIn('no-store',confirmed['Cache-Control'])
  state=call('bank_reconciliation_state',{'account_id':str(self.case.a.pk),'source_digest':hashlib.sha256(self.bank.csv.encode()).hexdigest()},'get');self.assertEqual(state.status_code,200,state.data);self.assertTrue(state.data['applied']['reconciliation_confirmed'])
 def test_another_actor_cannot_confirm_or_release_an_existing_review(self):
  review=self.review()
  with self.assertRaises(AccountingError):self.confirm(review,actor=self.case.other)
  confirmed=self.confirm(review);release=self.release_review(confirmed)
  with self.assertRaises(AccountingError):self.release(release,actor=self.case.other)
 def test_conflicting_release_cannot_overwrite_a_confirmed_release(self):
  confirmed=self.confirm(self.review());one=self.release_review(confirmed);two=self.release_review(confirmed,evidence_digest='c'*64)
  self.release(one)
  with self.assertRaises(AccountingError):self.release(two)
 def test_inactive_account_preserves_historical_recovery(self):
  from apps.core_erp.accounting.models import Account
  confirmed=self.confirm(self.review());Account.plain_objects.filter(pk=self.case.a.pk).update(is_active=False)
  state=self.state();self.assertEqual(state['applied']['reconciliation_id'],confirmed['reconciliation_id']);self.assertTrue(state['applied']['reconciliation_confirmed'])
 def test_foreign_company_cannot_confirm_the_statement(self):
  review=self.review()
  with self.assertRaises(AccountingError):engine.confirm_reconciliation(self.case.foreign.pk,actor=self.case.user,statement_id=review['statement_id'],review_id=review['review_id'],confirmed=True)
 def test_revoked_identity_is_denied_by_actual_http_boundary(self):
  from apps.turismo.models import VerifiedCompanyLink
  from django.utils import timezone
  VerifiedCompanyLink.objects.filter(provider=self.case.provider).update(revoked_at=timezone.now())
  request=APIRequestFactory().get('/fixture/',{'provider_id':str(self.case.provider.pk)});force_authenticate(request,user=self.case.user)
  response=PlanCuentaViewSet.as_view({'get':'bank_reconciliation_sources'})(request);self.assertEqual(response.status_code,403);self.assertIn('no-store',response['Cache-Control'])
if __name__=='__main__':unittest.main()
