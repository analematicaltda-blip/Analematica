"""Append-only correction of the latest active native return; no capacity guessing."""
import runpy,unittest,uuid
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_purchase_return_check.py')),run_name='return_void_fixture')
from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_return_voids as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.accounting.tax_register import reconcile_tax_register
from apps.core_erp.outbox_models import OutboxEvent
class ReturnVoidChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['PurchaseReturnChecks']();self.base.setUp();self.review_return=self.base.review();self.applied=self.base.post(self.review_return);self.target=self.review_return['return_id'];self.scope=self.base.scope
 def review(self,**kw):
  return engine.review(**self.scope,**{'return_id':self.target,'request_id':str(uuid.uuid4()),'entry_date':self.base.base.case.base.day.isoformat(),'reason_code':'DATA_ENTRY_ERROR','evidence_digest':'f'*64,'expected_revision':self.base.state()['revision'],'confirmed':True,**kw})
 def post(self,r,**kw):return engine.post(**self.scope,review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def test_counter_post_restores_capacity_and_input_tax_keeps_originals(self):
  before={str(j.pk):j.system_hash for j in JournalEntry.plain_objects.filter(tenant=self.base.base.company)};r=self.post(self.review());self.assertEqual(r['remaining']['net'],'100.00');self.assertEqual(r['returned']['net'],'0.00');self.assertTrue(r['returns'][0]['reversed']);self.assertEqual(r['returns'][0]['reversal_journal_id'],r['journal_id'])
  for key,value in before.items():self.assertEqual(JournalEntry.plain_objects.get(pk=key).system_hash,value)
  day=self.base.base.case.base.day.isoformat();tax=reconcile_tax_register(self.base.base.company.pk,account_id=str(self.base.base.case.input_tax.pk),since=day,until=day);self.assertEqual(tax['tax_by_kind']['INPUT_TAX'],'19.00');self.assertFalse(r['money_transferred']);self.assertFalse(r['fiscal_document_created'])
 def test_retry_posts_only_one_correction(self):
  r=self.review();a=self.post(r);count=JournalEntry.plain_objects.count();b=self.post(r);self.assertTrue(b['replayed']);self.assertEqual(a['journal_id'],b['journal_id']);self.assertEqual(count,JournalEntry.plain_objects.count())
 def test_capacity_can_be_used_by_new_return_but_document_stays_reserved(self):
  self.post(self.review())
  with self.assertRaises(AccountingError):self.base.review(document_digest=self.review_return['preview']['document_digest'])
  r=self.base.post(self.base.review('100.00'));self.assertEqual(r['remaining']['net'],'0.00');self.assertEqual(r['returned']['tax'],'19.00');self.assertEqual(r['revision'],2)
 def test_only_latest_active_return_can_be_corrected(self):
  second=self.base.review('10.00');self.base.post(second)
  with self.assertRaises(AccountingError):self.review()
  self.post(self.review(return_id=second['return_id']));self.post(self.review());self.assertEqual(self.base.state()['remaining']['net'],'100.00')
 def test_correction_preserves_cumulative_rounding_for_replacement(self):
  second=self.base.review('33.33');self.base.post(second);self.post(self.review(return_id=second['return_id']));self.base.post(self.base.review('75.00'));s=self.base.state();self.assertEqual(s['returned']['withholding'],'2.50');self.assertTrue(all(v=='0.00' for v in s['remaining'].values()))
 def test_old_return_review_is_stale_even_if_return_count_did_not_change(self):
  pending=self.base.review('75.00');self.post(self.review())
  with self.assertRaises(AccountingError):self.base.post(pending)
 def test_new_return_invalidates_pending_correction(self):
  pending=self.review();self.base.post(self.base.review('10.00'))
  with self.assertRaises(AccountingError):self.post(pending)
 def test_both_confirmations_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.post(r,confirmed=False)
 def test_missing_correction_proof_does_not_release_capacity_silently(self):
  self.post(self.review());OutboxEvent.objects.filter(event_type=engine.returns.VOIDED).delete()
  with self.assertRaises(AccountingError):self.base.state()
 def test_failed_proof_rolls_back_correction_journal_and_capacity(self):
  r=self.review();count=JournalEntry.plain_objects.count()
  with patch.object(engine.returns,'store',side_effect=AccountingError('synthetic store failure')):
   with self.assertRaises(AccountingError):self.post(r)
  self.assertEqual(count,JournalEntry.plain_objects.count());self.assertEqual(self.base.state()['remaining']['net'],'75.00')
 def test_generic_reversal_cannot_reverse_correction(self):
  r=self.post(self.review())
  with self.assertRaises(AccountingError):engine.LedgerEngine.reverse_entry(r['journal_id'],tenant_id=self.base.base.company.pk,actor=self.base.base.actor)
 def test_closed_period_and_invalid_reason_rejected(self):
  with self.assertRaises(AccountingError):self.review(reason_code='AUTO_APPROVED')
  r=self.review();engine.FiscalPeriod.plain_objects.filter(tenant=self.base.base.company).update(status='closed')
  with self.assertRaises(AccountingError):self.post(r)
 def test_expired_review_cannot_correct(self):
  from datetime import timedelta
  from django.utils import timezone
  r=self.review()
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=16)):
   with self.assertRaises(AccountingError):self.post(r)
 def test_changed_administrative_source_can_still_correct_historical_error(self):
  from apps.prestadores.mi_negocio.gestion_contable.compras.models import FacturaCompra
  FacturaCompra.objects.filter(pk=self.base.capture['invoice_id']).update(estado='ANULADA')
  r=self.post(self.review());self.assertEqual(r['remaining']['net'],'100.00');self.assertFalse(r['money_transferred'])
if __name__=='__main__':unittest.main()
