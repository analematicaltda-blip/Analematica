"""Native partial returns preserve source and conserve balances/rounding."""
import runpy,unittest,uuid,copy
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_native_purchase_check.py')),run_name='purchase_return_fixture')
from apps.prestadores.mi_negocio.gestion_contable.compras import purchase_returns as engine
from apps.core_erp.accounting.models import JournalEntry
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
class PurchaseReturnChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['NativePurchaseChecks']();self.base.setUp();self.capture=self.base.capture();self.original=self.base.post(self.capture,self.base.review(self.capture));self.scope={**self.base.scope,'invoice_id':self.capture['invoice_id']}
 def state(self):return engine.state(**self.scope)
 def review(self,amount='25.00',**kw):
  args={'return_id':str(uuid.uuid4()),'net_amount':amount,'entry_date':self.base.case.base.day.isoformat(),'document_digest':uuid.uuid4().hex*2,'evidence_digest':'d'*64,'expected_revision':self.state()['revision'],'confirmed':True};args.update(kw);return engine.review(**self.scope,**args)
 def post(self,r,**kw):return engine.post(**self.scope,review_id=r['review_id'],confirmed=kw.get('confirmed',True))
 def test_partial_then_remaining_matches_original_without_editing_it(self):
  original=JournalEntry.plain_objects.get(pk=self.original['journal_id']).system_hash;r=self.review();self.assertEqual(r['preview']['totals']['tax'],'4.75');a=self.post(r);self.assertEqual(a['remaining']['net'],'75.00');b=self.post(self.review('75.00'));self.assertEqual(b['remaining']['net'],'0.00');self.assertEqual(b['remaining']['tax'],'0.00');self.assertEqual(JournalEntry.plain_objects.get(pk=self.original['journal_id']).system_hash,original);self.assertFalse(b['money_transferred'])
 def test_retry_does_not_post_again(self):
  r=self.review();a=self.post(r);count=JournalEntry.plain_objects.count();b=self.post(r);self.assertEqual(a['journal_id'],b['journal_id']);self.assertTrue(b['replayed']);self.assertEqual(count,JournalEntry.plain_objects.count())
 def test_two_confirmations_and_stale_capacity(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  a=self.review('60.00');b=self.review('60.00')
  with self.assertRaises(AccountingError):self.post(a,confirmed=False)
  self.post(a)
  with self.assertRaises(AccountingError):self.post(b)
  self.assertEqual(self.state()['remaining']['net'],'40.00')
 def test_over_return_zero_and_binary_float_rejected(self):
  for value in ['101.00','0.00',25.0]:
   with self.assertRaises((AccountingError,ValueError)):self.review(value)
 def test_return_and_original_cannot_be_generically_reversed(self):
  r=self.post(self.review())
  for journal in [r['journal_id'],self.original['journal_id']]:
   with self.assertRaises(AccountingError):LedgerEngine.reverse_entry(journal,tenant_id=self.base.company.pk,actor=self.base.actor)
 def test_missing_return_origin_cannot_free_capacity(self):
  self.post(self.review());OutboxEvent.objects.filter(event_type=engine.POSTED).delete()
  with self.assertRaises(AccountingError):self.state()
 def test_tax_register_accounts_for_partial_return(self):
  self.post(self.review());r=fixture['reconcile_tax_register'](self.base.company.pk,account_id=str(self.base.case.input_tax.pk),since=self.base.case.base.day.isoformat(),until=self.base.case.base.day.isoformat());self.assertEqual(r['tax_by_kind']['INPUT_TAX'],'14.25');self.assertEqual(r['unattributed_normal_movement'],'0.00')
 def test_atomic_failure_cannot_leave_journal(self):
  from unittest.mock import patch
  r=self.review();before=JournalEntry.plain_objects.count()
  with patch.object(engine,'store',side_effect=AccountingError('test failure')):
   with self.assertRaises(AccountingError):self.post(r)
  self.assertEqual(before,JournalEntry.plain_objects.count());self.assertEqual(self.state()['returned']['net'],'0.00')
 def test_cumulative_rounding_conserves_last_cent(self):
  for amount in ['33.33','33.33','33.34']:self.post(self.review(amount))
  s=self.state();self.assertEqual(s['returned']['tax'],'19.00');self.assertEqual(s['returned']['withholding'],'2.50');self.assertTrue(all(v=='0.00' for v in s['remaining'].values()))
 def test_full_native_reversal_review_is_blocked_after_partial_return(self):
  self.post(self.review())
  with self.assertRaises(AccountingError):self.base.reverse_review(self.capture)
 def test_source_change_and_duplicate_return_document_are_blocked(self):
  r=self.review();self.post(r)
  with self.assertRaises(AccountingError):self.review(document_digest=r['preview']['document_digest'])
  fixture['FacturaCompra'].objects.filter(pk=self.capture['invoice_id']).update(estado='PAGADA')
  with self.assertRaises(AccountingError):self.review()
 def test_foreign_owner_and_reused_review_identity_are_blocked(self):
  from rest_framework.exceptions import PermissionDenied
  from django.contrib.auth import get_user_model
  other=get_user_model().objects.filter(is_active=True).exclude(pk=self.base.actor.pk).first();self.assertIsNotNone(other)
  with self.assertRaises(PermissionDenied):engine.state(actor=other,provider_id=self.base.provider.pk,invoice_id=self.capture['invoice_id'])
  args={'return_id':str(uuid.uuid4()),'net_amount':'25.00','entry_date':self.base.case.base.day.isoformat(),'document_digest':uuid.uuid4().hex*2,'evidence_digest':'d'*64,'expected_revision':0,'confirmed':True};a=engine.review(**self.scope,**args);self.assertEqual(a,engine.review(**self.scope,**args))
  with self.assertRaises(AccountingError):engine.review(**self.scope,**{**args,'net_amount':'26.00'})
 def test_closed_return_period_blocks_post_without_journal(self):
  r=self.review();before=JournalEntry.plain_objects.count();engine.FiscalPeriod.plain_objects.filter(tenant=self.base.company).update(status='closed')
  with self.assertRaises(AccountingError):self.post(r)
  self.assertEqual(before,JournalEntry.plain_objects.count())
 def test_posted_account_role_change_is_blocked_before_return(self):
  r=self.review();before=JournalEntry.plain_objects.count()
  with self.assertRaises(AccountingError):engine.Account.plain_objects.filter(pk=self.base.case.input_tax.pk).update(type='LIABILITY')
  account=engine.Account.plain_objects.get(pk=self.base.case.input_tax.pk);self.assertEqual(account.type,'ASSET');self.assertEqual(before,JournalEntry.plain_objects.count())
  self.post(r);self.assertEqual(before+1,JournalEntry.plain_objects.count())
 def test_expired_return_review_requires_fresh_review(self):
  from unittest.mock import patch
  from datetime import timedelta
  from django.utils import timezone
  r=self.review()
  with patch.object(engine.timezone,'now',return_value=timezone.now()+timedelta(minutes=16)):
   with self.assertRaises(AccountingError):self.post(r)
 def test_return_before_original_date_is_rejected(self):
  from datetime import timedelta
  with self.assertRaises(AccountingError):self.review(entry_date=(self.base.case.base.day-timedelta(days=1)).isoformat())
 def test_invoice_changed_after_return_review_cannot_post(self):
  r=self.review();before=JournalEntry.plain_objects.count();fixture['FacturaCompra'].objects.filter(pk=self.capture['invoice_id']).update(notas='Changed synthetic source')
  with self.assertRaises(AccountingError):self.post(r)
  self.assertEqual(before,JournalEntry.plain_objects.count());self.assertEqual(self.state()['returned']['net'],'0.00')
 def test_missing_document_claim_does_not_free_return_capacity(self):
  self.post(self.review());OutboxEvent.objects.filter(event_type=engine.DOCUMENT).delete()
  with self.assertRaises(AccountingError):self.state()
if __name__=='__main__':unittest.main()
