"""Coverage and decisions cannot claim a complete bank reconciliation falsely."""
import unittest,copy
from app.services.bank_resolution_contract import result,preview
class BankResolutionContractTests(unittest.TestCase):
 def data(self):return {'period_assessment':None,'period_source_current':None,'period_reconciled':False,'period_requires_review':False,'coverage':{'total_rows':2,'matched_rows':1,'unresolved_rows':1,'matched_in':'10.00','matched_out':'0.00','unresolved_in':'0.00','unresolved_out':'2.00'},'matched_rows':1,'fully_reconciled':False,'associations_confirmed':True,'reconciliation_confirmed':False,'released':False,'requires_review':False}
 def test_partial_associations_are_valid_without_full_claim(self):result(self.data())
 def test_partial_statement_cannot_be_presented_complete(self):
  for field in ('fully_reconciled','reconciliation_confirmed'):
   d=self.data();d[field]=True
   with self.assertRaises(ValueError):result(d)
 def test_boolean_counts_and_floating_money_rejected(self):
  for key,value in [('unresolved_rows',True),('unresolved_out',2.0),('total_rows',3)]:
   d=self.data();d['coverage'][key]=value
   with self.assertRaises(ValueError):result(d)
 def test_released_or_stale_associations_cannot_remain_qualified(self):
  for change in [{'released':True},{'requires_review':True}]:
   with self.assertRaises(ValueError):result({**self.data(),**change})
 def test_review_decisions_and_totals_must_match_exactly(self):
  p={'coverage':self.data()['coverage'],'rows':[{'row':1,'ledger_line_id':'synthetic-line','direction':'IN','amount':'10.00'}],'differences':[{'row':2,'reason_code':'BANK_FEE_UNPOSTED','direction':'OUT','amount':'2.00'}]};decisions=[{'row':1,'ledger_line_id':'synthetic-line','reason_code':None},{'row':2,'ledger_line_id':None,'reason_code':'BANK_FEE_UNPOSTED'}];preview(p,decisions)
  for change in [{'amount':'3.00'},{'reason_code':'UNIDENTIFIED'}]:
   bad=copy.deepcopy(p);bad['differences'][0].update(change)
   with self.assertRaises(ValueError):preview(bad,decisions)
 def test_complete_statement_requires_no_differences(self):
  d=self.data();d['coverage'].update(total_rows=1,unresolved_rows=0,unresolved_out='0.00');d.update(fully_reconciled=True,reconciliation_confirmed=True);result(d)
 def assessment(self):
  terms={'since':'2026-11-01','until':'2026-11-09','opening':'0.00','closing':'10.00','statement_complete':True,'evidence_digest':'a'*64}
  return {'schema':'sgacd-bank-period-assessment-v1','terms':terms,'currency':'COP','scope':'DECLARED_STATEMENT_AND_POSTED_CASH_ACCOUNT','source_independently_verified':False,'ledger_digest':'a'*64,'policy_digest':'b'*64,'bank_in':'10.00','bank_out':'0.00','ledger_opening':'0.00','ledger_closing':'10.00','ledger_in':'10.00','ledger_out':'0.00','opening_difference':'0.00','closing_difference':'0.00','flow_difference':'0.00','unmatched_ledger_line_ids':[],'ledger_history_rows':1,'ledger_period_rows':1,'unresolved_bank_rows':0,'balances_match':True,'eligible_for_period_reconciliation':True}
 def test_period_arithmetic_mismatch_rejected(self):
  from app.services.bank_resolution_contract import period
  a=self.assessment();period(a,a['terms']);a['ledger_closing']='11.00'
  with self.assertRaises(ValueError):period(a,a['terms'])
 def test_zero_balance_difference_cannot_hide_omitted_ledger_lines(self):
  import uuid
  from app.services.bank_resolution_contract import period
  a=self.assessment();a['unmatched_ledger_line_ids']=[str(uuid.uuid4())]
  with self.assertRaises(ValueError):period(a,a['terms'])
 def test_stale_period_cannot_claim_reconciled(self):
  d=self.data();d['coverage'].update(total_rows=1,unresolved_rows=0,unresolved_out='0.00');d.update(fully_reconciled=True,reconciliation_confirmed=True,period_assessment=self.assessment(),period_source_current=False,period_requires_review=True,period_reconciled=True)
  with self.assertRaises(ValueError):result(d)
 def test_unrequested_period_cannot_claim_balances(self):
  d=self.data();d.update(period_reconciled=True)
  with self.assertRaises(ValueError):result(d)
if __name__=='__main__':unittest.main()
