"""Grouped/split statement evidence with real disposable cash journals."""
import runpy,unittest,uuid,copy
from pathlib import Path
from unittest.mock import patch
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_period_check.py')),run_name='groups_fixture')
from apps.core_erp.accounting import bank_groups as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import LedgerEntry
from apps.core_erp.outbox_models import OutboxEvent
class GroupChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['BankPeriodChecks']();self.base.setUp();self.case=self.base.case;self.bank=self.base.base
  line=LedgerEntry.plain_objects.get(journal_entry=self.bank.bank.entry,account=self.case.a)
  self.line=str(line.pk);self.header='transaction_id,date,direction,amount,currency\n'
  self.csv=self.header+f'split-a,{self.base.day},IN,4.00,COP\nsplit-b,{self.base.day},IN,6.00,COP\n'
  self.args={'actor':self.case.user,'account_id':str(self.case.a.pk),'csv_text':self.csv,'groups':[{'rows':[1,2],'ledger_line_ids':[self.line]}],'differences':[],'evidence_digest':'a'*64,'confirmed':True}
 def review(self,**kw):return engine.review_groups(self.case.tenant.pk,**{**self.args,**kw})
 def confirm(self,r,**kw):return engine.confirm_groups(self.case.tenant.pk,**{'actor':self.case.user,'review_id':r['review_id'],'confirmed':True,**kw})
 def test_split_rows_balance_once_and_replay(self):
  r=self.review();a=self.confirm(r);b=self.confirm(r);self.assertTrue(a['fully_reconciled']);self.assertTrue(b['replayed']);self.assertEqual(a['reconciliation_id'],b['reconciliation_id']);self.assertEqual(a['coverage']['matched_rows'],2);self.assertFalse(a['money_transferred'])
 def test_partial_ledger_allocation_keeps_remainder_and_reserves_line(self):
  csv=self.header+f'partial,{self.base.day},IN,4.00,COP\n'
  group={'rows':[1],'ledger_line_ids':[self.line],'ledger_allocations':{self.line:'4.00'},'remainder_reason':'TIMING_DIFFERENCE'}
  r=self.review(csv_text=csv,groups=[group]);a=self.confirm(r);self.assertFalse(a['fully_reconciled']);self.assertEqual(a['ledger_remainders'][0]['amount'],'6.00')
  with self.assertRaises(AccountingError):self.bank.review()
 def test_grouped_ledger_lines(self):
  extra=self.base.post_cash('3.00');line=LedgerEntry.plain_objects.get(journal_entry=extra,account=self.case.a)
  r=self.review(csv_text=self.header+f'group,{self.base.day},IN,13.00,COP\n',groups=[{'rows':[1],'ledger_line_ids':[self.line,str(line.pk)]}]);self.assertTrue(self.confirm(r)['fully_reconciled'])
 def test_partial_group_retains_difference(self):
  csv=self.csv+f'unknown,{self.base.day},OUT,2.00,COP\n'
  r=self.review(csv_text=csv,differences=[{'row':3,'reason_code':'UNIDENTIFIED'}]);a=self.confirm(r);self.assertFalse(a['fully_reconciled']);self.assertEqual(a['coverage']['unresolved_rows'],1)
 def test_duplicate_rows_lines_and_unequal_amounts_denied(self):
  for changes in [{'groups':[{'rows':[1,1],'ledger_line_ids':[self.line]}]},{'groups':[{'rows':[1,2],'ledger_line_ids':[self.line,self.line]}]},{'csv_text':self.csv.replace('6.00','5.00')}]:
   with self.assertRaises(AccountingError):self.review(**changes)
 def test_existing_individual_claim_blocks_group(self):
  self.bank.confirm(self.bank.review())
  with self.assertRaises(AccountingError):self.review()
 def test_group_claim_blocks_individual_and_other_source(self):
  self.confirm(self.review())
  with self.assertRaises(AccountingError):self.bank.review()
  with self.assertRaises(AccountingError):self.review(csv_text=self.csv.replace('split-','other-'))
 def test_changed_line_blocks_confirmation(self):
  r=self.review();LedgerEntry.plain_objects.filter(pk=self.line).update(description='Synthetic tamper')
  with self.assertRaises(AccountingError):self.confirm(r)
 def test_failed_claim_rolls_back_and_two_confirmations_required(self):
  with self.assertRaises(AccountingError):self.review(confirmed=False)
  r=self.review()
  with self.assertRaises(AccountingError):self.confirm(r,confirmed=False)
  before=OutboxEvent.objects.count();original=OutboxEvent.objects.create
  def fail(**kw):
   if kw.get('event_type')==engine.APPLIED:raise RuntimeError('Synthetic proof failure')
   return original(**kw)
  with patch.object(OutboxEvent.objects,'create',side_effect=fail):
   with self.assertRaises(RuntimeError):self.confirm(r)
  self.assertEqual(before,OutboxEvent.objects.count());self.assertTrue(self.confirm(r)['fully_reconciled'])
 def test_group_history_release_and_reallocation(self):
  r=self.review();self.confirm(r);state=engine.group_state(self.case.tenant.pk,actor=self.case.user,review_id=r['review_id']);self.assertFalse(state['confirmations_restored']);self.assertTrue(state['applied']['fully_reconciled'])
  release=engine.review_group_release(self.case.tenant.pk,actor=self.case.user,review_id=r['review_id'],reason_code='WRONG_MATCH',evidence_digest='f'*64,confirmed=True)
  with self.assertRaises(AccountingError):engine.confirm_group_release(self.case.tenant.pk,actor=self.case.user,review_id=release['review_id'],confirmed=False)
  result=engine.confirm_group_release(self.case.tenant.pk,actor=self.case.user,review_id=release['review_id'],confirmed=True);self.assertTrue(result['released']);self.assertFalse(result['fully_reconciled'])
  self.assertTrue(self.bank.confirm(self.bank.review())['fully_reconciled'])
 def test_group_http_has_scoped_no_store_response(self):
  call=self.case.call;payload={k:v for k,v in self.args.items() if k!='actor'}
  r=call('review_bank_groups','post',payload);self.assertEqual(r.status_code,200,r.data)
  a=call('confirm_bank_groups','post',{'review_id':r.data['review_id'],'confirmed':True});self.assertEqual(a.status_code,200,a.data);self.assertIn('no-store',a['Cache-Control'])
 def original_review(self):
  from apps.core_erp.accounting import bank_grouped
  return bank_grouped.review(self.case.tenant.pk,actor=self.case.user,account_id=str(self.case.a.pk),csv_text=self.csv,groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1,2],'ledger_line_ids':[self.line]}],evidence_digest='b'*64,expected_revision=0,confirmed=True)
 def test_published_group_reserves_original_protocol_capacity(self):
  self.confirm(self.review())
  with self.assertRaises(AccountingError):self.original_review()
 def test_original_group_blocks_published_protocol(self):
  from apps.core_erp.accounting import bank_grouped
  r=self.original_review();bank_grouped.confirm(self.case.tenant.pk,actor=self.case.user,statement_id=r['statement_id'],review_id=r['review_id'],confirmed=True)
  with self.assertRaises(AccountingError):self.review()
 def test_released_published_group_restores_original_capacity(self):
  r=self.review();self.confirm(r)
  release=engine.review_group_release(self.case.tenant.pk,actor=self.case.user,review_id=r['review_id'],reason_code='WRONG_MATCH',evidence_digest='b'*64,confirmed=True)
  engine.confirm_group_release(self.case.tenant.pk,actor=self.case.user,review_id=release['review_id'],confirmed=True)
  self.assertIn('review_id',self.original_review())
if __name__=='__main__' :unittest.main()
