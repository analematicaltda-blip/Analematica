"""Full native reversal only after verified counter-posting of every return."""
import runpy,unittest,uuid,copy
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_purchase_return_void_check.py')),run_name='return_final_fixture')
from apps.core_erp.accounting import native_return_reversal as gate
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.tax_register import reconcile_tax_register
from apps.core_erp.outbox_models import OutboxEvent
class FinalReturnReversalChecks(unittest.TestCase):
 def setUp(self):
  self.void=fixture['ReturnVoidChecks']();self.void.setUp();self.returns=self.void.base;self.native=self.returns.base;self.capture=self.returns.capture
 def corrected(self):return self.void.post(self.void.review())
 def review(self):return self.native.reverse_review(self.capture)
 def post(self,review):return self.native.reverse(self.capture,review)
 def test_corrected_returns_allow_two_step_full_reversal_and_tax_zero(self):
  self.corrected();before={str(j.pk):j.system_hash for j in JournalEntry.plain_objects.filter(tenant=self.native.company)};review=self.review();result=self.post(review);self.assertTrue(result['ledger_written']);self.assertFalse(result['money_transferred']);self.assertFalse(result['fiscal_document_created'])
  for identifier,digest in before.items():self.assertEqual(JournalEntry.plain_objects.get(pk=identifier).system_hash,digest)
  state=self.returns.state();self.assertTrue(state['original_reversed']);self.assertEqual(state['remaining']['net'],'0.00');self.assertEqual(state['returned']['net'],'0.00');self.assertTrue(state['returns'][0]['reversed']);self.assertFalse(state['confirmations_restored'])
  day=self.native.case.base.day.isoformat();tax=reconcile_tax_register(self.native.company.pk,account_id=str(self.native.case.input_tax.pk),since=day,until=day);self.assertEqual(tax['tax_by_kind']['INPUT_TAX'],'0.00');self.assertEqual(tax['unattributed_normal_movement'],'0.00')
 def test_active_return_still_blocks_full_reversal_review(self):
  with self.assertRaises(AccountingError):self.review()
 def test_direct_generic_reversal_remains_blocked_after_corrections(self):
  self.corrected()
  with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(self.returns.original['journal_id'],tenant_id=self.native.company.pk,actor=self.native.actor)
 def test_retry_recovers_identical_full_reversal_without_second_post(self):
  self.corrected();review=self.review();a=self.post(review);count=JournalEntry.plain_objects.count();b=self.post(review);self.assertTrue(b['replayed']);self.assertEqual(a['journal_id'],b['journal_id']);self.assertEqual(count,JournalEntry.plain_objects.count())
 def test_new_return_makes_full_reversal_review_stale(self):
  self.corrected();review=self.review();self.returns.post(self.returns.review('10.00'))
  with self.assertRaises(AccountingError):self.post(review)
 def test_neutral_return_and_correction_cycle_also_invalidates_review(self):
  self.corrected();review=self.review();r=self.returns.review('10.00');self.returns.post(r);self.void.post(self.void.review(return_id=r['return_id']))
  with self.assertRaises(AccountingError):self.post(review)
 def test_review_created_before_any_returns_cannot_adopt_later_history(self):
  # A second native invoice makes the old no-history review explicit.
  c=self.native.capture(request_id=str(uuid.uuid4()),number='SYNTHETIC-SECOND',document_digest=uuid.uuid4().hex*2);self.native.post(c,self.native.review(c));old=self.native.reverse_review(c)
  engine=fixture['engine'].returns;scope={**self.native.scope,'invoice_id':c['invoice_id']};r=engine.review(**scope,return_id=str(uuid.uuid4()),net_amount='1.00',entry_date=self.native.case.base.day.isoformat(),document_digest=uuid.uuid4().hex*2,evidence_digest='a'*64,expected_revision=0,confirmed=True);engine.post(**scope,review_id=r['review_id'],confirmed=True)
  v=fixture['engine'].review(**scope,return_id=r['return_id'],request_id=str(uuid.uuid4()),entry_date=self.native.case.base.day.isoformat(),reason_code='DATA_ENTRY_ERROR',evidence_digest='b'*64,expected_revision=1,confirmed=True);fixture['engine'].post(**scope,review_id=v['review_id'],confirmed=True)
  with self.assertRaises(AccountingError):self.native.reverse(c,old)
 def test_missing_correction_proof_never_unlocks_full_reversal(self):
  self.corrected();OutboxEvent.objects.filter(event_type=fixture['engine'].returns.VOIDED).delete()
  with self.assertRaises(AccountingError):self.review()
 def test_forged_internal_snapshot_cannot_bypass_gate(self):
  self.corrected();identifier=self.returns.original['journal_id'];fake={'document_id':self.capture['document_id'],'history_digest':'0'*64}
  with gate._permit(self.native.company,identifier,self.native.actor.pk,fake):
   with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(identifier,tenant_id=self.native.company.pk,actor=self.native.actor)
 def test_post_failure_resets_permit_and_rolls_back_full_reversal(self):
  self.corrected();review=self.review();count=JournalEntry.plain_objects.count();commercial=fixture['engine'].returns.ledger
  with patch.object(commercial,'save',side_effect=AccountingError('synthetic save failure')):
   with self.assertRaises(AccountingError):self.post(review)
  self.assertEqual(count,JournalEntry.plain_objects.count());self.assertIsNone(gate._SCOPE.get());self.assertFalse(self.returns.state()['original_reversed'])
 def test_return_and_correction_journals_never_allow_generic_reversal(self):
  corrected=self.corrected()
  for identifier in [self.void.applied['journal_id'],corrected['journal_id']]:
   with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(identifier,tenant_id=self.native.company.pk,actor=self.native.actor)
 def test_new_return_after_full_reversal_is_rejected(self):
  self.corrected();self.post(self.review())
  with self.assertRaises(AccountingError):self.returns.review('1.00')
 def test_missing_namespace_cannot_make_adjustment_look_generic(self):
  journal=JournalEntry.plain_objects.get(pk=self.void.applied['journal_id']);journal.financial_event_id='misclassified-event'
  with self.assertRaises(AccountingError):gate.require(self.native.company,journal,self.native.actor.pk)
if __name__=='__main__':unittest.main()
