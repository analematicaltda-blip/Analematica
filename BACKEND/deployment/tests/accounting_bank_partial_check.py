"""Partial cash matching across statements with exact remaining capacity."""
import runpy,unittest,uuid,copy
from pathlib import Path
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_grouped_check.py')),run_name='partial_bank_fixture')
from apps.core_erp.accounting import bank_grouped as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
class PartialBankChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['GroupedBankChecks']();self.base.setUp();self.case=self.base.case;self.line=self.base.line;self.day=self.base.base.bank.day
 def text(self,name,amount,day=None):return 'transaction_id,date,direction,amount,currency\n'+name+','+(day or self.day)+',IN,'+amount+',COP\n'
 def source(self,name='preview',amount='4.00',**kw):return engine.sources(self.case.tenant.pk,actor=self.case.user,account_id=str(self.case.a.pk),csv_text=self.text(name,amount),**kw)
 def review(self,name='part-a',amount='4.00',**kw):
  args={**self.base.args,'csv_text':self.text(name,amount),'groups':[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':self.line,'amount':amount}]}],'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True};args.update(kw);return engine.review(self.case.tenant.pk,**args)
 def balance(self,r):return next(row for row in r['line_balances'] if row['ledger_line_id']==self.line)
 def test_four_then_six_across_two_statements_fully_consumes_ten_once(self):
  before=self.base.base.counts();a=self.base.confirm(self.review());self.assertEqual(self.balance(a)['available_amount'],'6.00');source=self.source();self.assertEqual(source['ledger_lines'][0]['reserved_amount'],'4.00');b=self.base.confirm(self.review('part-b','6.00'));self.assertEqual(self.balance(b)['available_amount'],'0.00');self.assertEqual(self.base.base.counts(),before);self.assertFalse(b['money_transferred']);self.assertFalse(b['period_reconciled'])
 def test_competing_six_plus_six_reviews_cannot_overallocate(self):
  first=self.review('a','6.00');second=self.review('b','6.00');self.base.confirm(first)
  with self.assertRaises(AccountingError):self.base.confirm(second)
  self.assertEqual(self.source()['ledger_lines'][0]['available_amount'],'4.00')
 def test_competing_four_plus_four_both_fit_and_leave_two(self):
  first=self.review('a','4.00');second=self.review('b','4.00');self.base.confirm(first);b=self.base.confirm(second);self.assertEqual(self.balance(b)['available_amount'],'2.00')
 def test_duplicate_bank_reference_cannot_consume_remaining_capacity(self):
  self.base.confirm(self.review())
  with self.assertRaises(AccountingError):self.review('part-a','6.00')
 def test_full_and_legacy_modes_cannot_reuse_partially_reserved_line(self):
  self.base.confirm(self.review())
  with self.assertRaises(AccountingError):self.base.base.review()
  with self.assertRaises(AccountingError):self.base.review()
 def test_release_reopens_only_its_own_amount(self):
  a=self.base.confirm(self.review('a','4.00'));self.base.confirm(self.review('b','6.00'));self.base.release(a);self.assertEqual(self.source()['ledger_lines'][0]['available_amount'],'4.00');c=self.base.confirm(self.review('c','4.00'));self.assertEqual(self.balance(c)['available_amount'],'0.00')
 def test_tampered_or_deleted_line_claim_cannot_free_capacity(self):
  a=self.base.confirm(self.review());claim=OutboxEvent.objects.filter(event_type=engine.legacy.CLAIM,payload__reconciliation_id=a['reconciliation_id'],payload__ledger_line_id=self.line).first();claim.delete()
  with self.assertRaises(AccountingError):self.source()
 def test_mutating_a_claim_index_does_not_make_capacity_reappear(self):
  a=self.base.confirm(self.review());claim=OutboxEvent.objects.filter(event_type=engine.legacy.CLAIM,payload__reconciliation_id=a['reconciliation_id'],payload__ledger_line_id=self.line).first();payload=copy.deepcopy(claim.payload);payload['ledger_line_id']=str(uuid.uuid4());OutboxEvent.objects.filter(pk=claim.pk).update(payload=payload)
  with self.assertRaises(AccountingError):self.source()
 def test_zero_float_or_overallocation_is_rejected(self):
  for amount in ['0.00',4.0,'11.00']:
   with self.assertRaises((AccountingError,ValueError)):self.review(amount='4.00' if isinstance(amount,float) else amount,groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':self.line,'amount':amount}]}])
 def test_one_line_can_be_distributed_to_two_groups_in_same_file(self):
  r=self.base.review(groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':self.line,'amount':'6.00'}]},{'group_id':str(uuid.uuid4()),'bank_rows':[2],'ledger_allocations':[{'ledger_line_id':self.line,'amount':'4.00'}]}]);a=self.base.confirm(r);self.assertEqual(self.balance(a)['available_amount'],'0.00')
 def test_explicit_historical_window_allows_prior_cash_date(self):
  yesterday=self.base.base.bank.entry.date-timedelta(days=1);self.case.period.period_start=yesterday;self.case.period.save()
  # Existing cash date is today; put the bank row one day later without future data.
  # Use an actual earlier cash posting and a current nonfuture bank row instead.
  from apps.core_erp.accounting.ledger_engine import LedgerEngine
  p=LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=yesterday,description='Synthetic prior-date cash',lines_data=[{'account':self.case.a,'debit':'20.00'},{'account':self.case.b,'credit':'20.00'}],actor=self.case.user,idempotency_key='prior-partial')
  source=self.source(ledger_since=yesterday.isoformat());line=next(r for r in source['ledger_lines'] if r['journal_id']==str(p.pk));groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':line['ledger_line_id'],'amount':'4.00'}]}]
  r=self.review(groups=groups,ledger_since=yesterday.isoformat());a=self.base.confirm(r);self.assertEqual(next(row for row in a['line_balances'] if row['ledger_line_id']==line['ledger_line_id'])['available_amount'],'16.00')
 def test_unknown_or_invalid_source_window_rejected(self):
  with self.assertRaises(AccountingError):self.source(ledger_since='1900-01-01')
 def test_replay_does_not_reserve_another_amount(self):
  r=self.review();a=self.base.confirm(r);b=self.base.confirm(r);self.assertEqual(a['reconciliation_id'],b['reconciliation_id']);self.assertTrue(b['replayed']);self.assertEqual(self.balance(b)['reserved_amount'],'4.00')
if __name__=='__main__':unittest.main()
