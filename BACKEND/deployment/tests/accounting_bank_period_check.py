"""Period balances/coverage must reconcile before qualification, no ledger writes."""
import runpy,unittest,copy,uuid
from pathlib import Path
from datetime import timedelta
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_reconciliation_check.py')),run_name='bank_period_fixture')
from apps.core_erp.accounting import bank_reconciliation as engine
from apps.core_erp.accounting.bank_period import signed,fmt
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.accounting.models import Account,JournalEntry
class BankPeriodChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['BankReconciliationTests']();self.base.setUp();self.case=self.base.case;self.day=self.base.bank.day
  self.period={'since':self.day,'until':self.day,'opening':'0.00','closing':'10.00','statement_complete':True,'evidence_digest':'e'*64}
 def review(self,**kw):return self.base.review(**{'period':self.period,**kw})
 def post_cash(self,amount='3.00',day=None):return LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=day or self.base.bank.entry.date,description='Synthetic additional bank cash',lines_data=[{'account':self.case.a,'debit':amount},{'account':self.case.b,'credit':amount}],actor=self.case.user,idempotency_key=str(uuid.uuid4()))
 def test_matching_complete_period_is_qualified_after_second_confirmation(self):
  before=self.base.counts();r=self.review();a=r['preview']['period_assessment'];self.assertEqual(a['ledger_opening'],'0.00');self.assertEqual(a['ledger_closing'],'10.00');self.assertTrue(a['eligible_for_period_reconciliation']);self.assertNotIn('period_reconciled',r)
  p=self.base.confirm(r);self.assertTrue(p['period_reconciled']);self.assertTrue(p['period_source_current']);self.assertFalse(p['bank_verified']);self.assertFalse(p['ledger_written']);self.assertEqual(before,self.base.counts());self.assertEqual(self.base.confirm(r)['reconciliation_id'],p['reconciliation_id'])
 def test_bank_arithmetic_mismatch_blocks_review(self):
  with self.assertRaises(AccountingError):self.review(period={**self.period,'closing':'11.00'})
 def test_no_complete_statement_declaration_or_missing_evidence(self):
  for change in [{'statement_complete':False},{'statement_complete':1},{'evidence_digest':'not-a-proof'}]:
   with self.assertRaises(AccountingError):self.review(period={**self.period,**change})
 def test_dates_must_contain_rows_and_not_be_future(self):
  for change in [{'since':(self.base.bank.entry.date+timedelta(days=1)).isoformat()},{'until':(self.base.bank.entry.date+timedelta(days=1)).isoformat()}]:
   with self.assertRaises(AccountingError):self.review(period={**self.period,**change})
 def test_equal_closing_does_not_hide_opening_difference(self):
  self.period.update(opening='1.00',closing='11.00');a=self.base.confirm(self.review());self.assertFalse(a['period_reconciled']);self.assertEqual(a['period_assessment']['opening_difference'],'1.00');self.assertEqual(a['period_assessment']['closing_difference'],'1.00')
 def test_unimported_cash_movement_prevents_complete_period(self):
  self.post_cash();r=self.review();p=self.base.confirm(r);self.assertTrue(p['fully_reconciled']);self.assertFalse(p['period_reconciled']);self.assertEqual(p['period_assessment']['closing_difference'],'-3.00');self.assertEqual(len(p['period_assessment']['unmatched_ledger_line_ids']),1)
 def test_offsetting_omitted_movements_cannot_hide_coverage_gaps(self):
  self.post_cash();LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=self.base.bank.entry.date,description='Synthetic opposite omitted cash',lines_data=[{'account':self.case.b,'debit':'3.00'},{'account':self.case.a,'credit':'3.00'}],actor=self.case.user,idempotency_key='opposite-omitted')
  p=self.base.confirm(self.review());a=p['period_assessment'];self.assertTrue(a['balances_match']);self.assertEqual(len(a['unmatched_ledger_line_ids']),2);self.assertFalse(p['period_reconciled'])
 def test_new_cash_after_review_blocks_confirmation_without_claims(self):
  r=self.review();self.post_cash()
  with self.assertRaises(AccountingError):self.base.confirm(r)
 def test_late_backdated_movement_invalidates_recorded_period(self):
  r=self.review();self.base.confirm(r);self.post_cash();p=self.base.confirm(r);self.assertFalse(p['period_source_current']);self.assertTrue(p['period_requires_review']);self.assertFalse(p['period_reconciled']);self.assertTrue(p['associations_confirmed'])
 def test_opening_uses_actual_prior_cash_history(self):
  prior=self.base.bank.entry.date-timedelta(days=1);self.case.period.period_start=prior;self.case.period.save();self.post_cash('5.00',prior);self.period.update(opening='5.00',closing='15.00');p=self.base.confirm(self.review());self.assertTrue(p['period_reconciled']);self.assertEqual(p['period_assessment']['ledger_opening'],'5.00')
 def test_inactive_account_invalidates_qualified_period(self):
  r=self.review();self.base.confirm(r);Account.plain_objects.filter(pk=self.case.a.pk).update(is_active=False);p=self.base.confirm(r);self.assertFalse(p['period_reconciled']);self.assertFalse(p['period_source_current'])
 def test_release_preserves_assessment_and_removes_qualification(self):
  p=self.base.confirm(self.review());released=self.base.release(self.base.release_review(p));self.assertTrue(released['released']);self.assertFalse(released['period_reconciled']);self.assertIsNotNone(released['period_assessment'])
 def test_unrequested_period_never_claims_balances_reconciled(self):
  p=self.base.confirm(self.base.review());self.assertIsNone(p['period_assessment']);self.assertFalse(p['period_reconciled']);self.assertIsNone(p['period_source_current'])
 def test_signed_balances_are_exact_and_negative_subunits_are_formatted_correctly(self):
  self.assertEqual(signed('-0.03'),-3);self.assertEqual(fmt(-3),'-0.03')
  for value in ['-0.00','01.00',1.0,True,'1e2',' 1.00']:
   with self.assertRaises(AccountingError):signed(value)
if __name__=='__main__':unittest.main()
