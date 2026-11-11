"""ACC-001 original criteria: executable acceptance, no external services needed."""
import runpy,unittest,uuid
from pathlib import Path
from decimal import Decimal,localcontext,Inexact,ROUND_DOWN
f=runpy.run_path(str(Path(__file__).with_name('accounting_posting_check.py')),run_name='acc001_fixture')
from django.utils import timezone
from apps.core_erp.accounting.validation import money,validate_lines
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry,FiscalPeriod,Account,ChartOfAccounts,AccountingEventReceipt,AccountingAuditLog
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.journal_service import JournalService
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
class ACC001Acceptance(unittest.TestCase):
 def setUp(self):self.case=f['PostingTests']();self.case.setUp();self.c=self.case
 def counts(self):return tuple(m.plain_objects.count() if hasattr(m,'plain_objects') else m.objects.count() for m in [JournalEntry,LedgerEntry,AccountingEventReceipt,AccountingAuditLog,OutboxEvent])
 def test_money_rejects_nonfinite_float_bool_fraction_and_overflow(self):
  for value in [True,False,0.1,float('nan'),float('inf'),'NaN','sNaN','Infinity','-Infinity','-0.01','0.001','9999999999999999.999','10000000000000000',None]:
   with self.subTest(value=repr(value)),self.assertRaises(AccountingError):money(value)
 def test_money_does_not_inherit_precision_rounding_or_traps(self):
  with localcontext() as ctx:
   ctx.prec=3;ctx.rounding=ROUND_DOWN;ctx.traps[Inexact]=True
   self.assertEqual(str(money('9999999999999999.99')),'9999999999999999.99')
   with self.assertRaises(AccountingError):money('123456.789')
   self.assertEqual(ctx.prec,3);self.assertTrue(ctx.traps[Inexact])
 def test_context_cannot_hide_one_cent_imbalance(self):
  with localcontext() as ctx:
   ctx.prec=6
   with self.assertRaises(AccountingError):validate_lines([{'debit':'1000000.00'},{'debit':'0.01'},{'credit':'1000000.00'}])
   self.assertEqual(len(validate_lines([{'debit':'1000000.00'},{'debit':'0.01'},{'credit':'1000000.01'}])),3)
 def test_aliases_cannot_hide_conflicting_or_invalid_amounts(self):
  for extra in [{'debit_amount':'9.99'},{'debit_amount':10.0},{'debit_amount':True}]:
   with self.assertRaises(AccountingError):validate_lines([{'debit':'10.00',**extra},{'credit':'10.00'}])
  self.assertEqual(validate_lines([{'debit':'10.00','debit_amount':'10'},{'credit':'10.00'}])[0]['debit'],Decimal('10.00'))
 def test_transaction_amount_cannot_be_silently_rounded_in_draft(self):
  before=self.counts()
  for amount in ['0.001',10.0,'NaN']:
   with self.assertRaises(AccountingError):JournalService.create_entry(str(self.c.tenant.pk),timezone.localdate(),'Invalid transaction amount',[{'account':self.c.a,'debit':'10.00','amount_transaction':amount},{'account':self.c.b,'credit':'10.00'}],created_by=self.c.user)
   self.assertEqual(self.counts(),before)
 def test_period_created_after_draft_blocks_posting_without_writes(self):
  entry=self.c.draft();before=self.counts();other=FiscalPeriod.plain_objects.create(tenant=self.c.tenant,period_start=self.c.period.period_start,period_end=self.c.period.period_end,status='open')
  with self.assertRaises(AccountingError):self.c.post(entry)
  self.assertEqual(self.counts(),before);entry.refresh_from_db();self.assertFalse(entry.is_posted)
  other.status='closed';other.save();self.assertTrue(self.c.post(entry).is_posted)
 def test_closed_period_replay_does_not_create_a_second_entry(self):
  entry=self.c.post(self.c.draft());before=self.counts();self.c.period.status='closed';self.c.period.save();self.assertEqual(self.c.post(entry).pk,entry.pk);self.assertEqual(self.counts(),before)
 def test_account_deactivated_after_draft_is_rechecked(self):
  entry=self.c.draft();before=self.counts();Account.plain_objects.filter(pk=self.c.a.pk).update(is_active=False)
  with self.assertRaises(AccountingError):self.c.post(entry)
  self.assertEqual(self.counts(),before)
 def test_foreign_chart_even_on_local_account_rejected(self):
  chart=ChartOfAccounts.plain_objects.create(tenant=self.c.foreign,name='Foreign chart');Account.plain_objects.filter(pk=self.c.a.pk).update(chart_of_accounts=chart);before=self.counts()
  with self.assertRaises(AccountingError):self.c.draft()
  self.assertEqual(self.counts(),before)
 def test_event_and_manual_posting_are_exact_under_hostile_context(self):
  self.c.a.code='111005';self.c.a.save();self.c.b.code='130505';self.c.b.save()
  with localcontext() as ctx:
   ctx.prec=6;ctx.rounding=ROUND_DOWN
   args={'tenant_id':self.c.tenant.pk,'entry_date':timezone.localdate(),'description':'Exact acceptance','lines_data':[{'account':self.c.a,'debit':'1000000.01'},{'account':self.c.b,'credit':'1000000.01'}],'actor':self.c.user,'idempotency_key':uuid.uuid4().hex}
   manual=LedgerEngine.post_lines(**args);event=LedgerEngine.post_event('PAYMENT_RECEIVED',{'tenant_id':str(self.c.tenant.pk),'financial_event_id':uuid.uuid4().hex,'amount':'1000000.01'},actor=self.c.user)
  for entry in [manual,event]:
   rows=list(LedgerEntry.plain_objects.filter(journal_entry=entry));self.assertEqual(sum(r.debit_amount for r in rows),Decimal('1000000.01'));self.assertEqual(sum(r.credit_amount for r in rows),Decimal('1000000.01'));self.assertEqual({r.amount_base for r in rows},{Decimal('1000000.01')})
if __name__=='__main__':unittest.main()
