"""No false financial authority, foreign sources or unbalanced group results."""
import unittest,uuid,copy,hashlib
from app.services.bank_group_contract import validate,body
class GroupContractChecks(unittest.TestCase):
 def setUp(self):
  self.context={'tenant_id':str(uuid.uuid4())};self.line=str(uuid.uuid4());self.group=str(uuid.uuid4());self.statement=str(uuid.uuid4())
  self.source={'company_id':self.context['tenant_id'],'bank_rows':[{'row':1,'date':'2026-11-09','direction':'IN','amount':'15.00'}],'ledger_lines':[{'ledger_line_id':self.line,'date':'2026-11-09','direction':'IN','amount':'15.00'}],'groups':[{'group_id':self.group,'bank_rows':[1],'ledger_line_ids':[self.line],'date':'2026-11-09','direction':'IN','amount':'15.00'}]}
 def test_balanced_group_contract(self):body(self.source,self.context)
 def test_group_cannot_hide_a_monetary_difference(self):
  for key in ('bank_rows','ledger_lines'):
   s=copy.deepcopy(self.source);s[key][0]['amount']='14.00'
   with self.assertRaises(ValueError):body(s,self.context)
 def test_uncovered_or_reused_rows_are_rejected(self):
  s=copy.deepcopy(self.source);s['groups']*=2
  with self.assertRaises(ValueError):body(s,self.context)
 def test_confirmed_metadata_never_claims_payment_or_period_reconciliation(self):
  data={'schema':'sgacd-bank-group-result-v1','company_id':self.context['tenant_id'],'reconciliation_id':str(uuid.uuid4()),'review_id':str(uuid.uuid4()),'statement_id':self.statement,'group_count':1,'bank_row_count':1,'ledger_line_count':1,'groups_confirmed':True,'requires_review':False,'released':False,'replayed':False,'period_reconciled':False,'ledger_written':False,'money_transferred':False,'bank_verified':False,'confirmations_restored':False};payload={'statement_id':self.statement};validate('confirm_bank_groups',data,payload,self.context)
  for change in [{'money_transferred':True},{'period_reconciled':True},{'released':True},{'company_id':str(uuid.uuid4())}]:
   with self.assertRaises(ValueError):validate('confirm_bank_groups',{**data,**change},payload,self.context)
 def partial_body(self):
  d=copy.deepcopy(self.source);d['ledger_since']='2026-11-09';d['allocation_totals']={self.line:'4.00'};d['bank_rows'][0]['amount']='4.00';d['ledger_lines'][0].update(available_amount='15.00',reserved_amount='0.00');d['groups'][0].update(amount='4.00',ledger_allocations=[{'ledger_line_id':self.line,'amount':'4.00'}]);return d
 def test_explicit_partial_body_conserves_own_amount_not_whole_line(self):body(self.partial_body(),self.context)
 def test_partial_totals_cannot_differ_from_selected_allocations(self):
  d=self.partial_body();d['allocation_totals'][self.line]='5.00'
  with self.assertRaises(ValueError):body(d,self.context)
 def test_partial_source_cannot_exceed_declared_available_capacity(self):
  d=self.partial_body();d['ledger_lines'][0]['available_amount']='3.00'
  with self.assertRaises(ValueError):body(d,self.context)
 def test_partial_date_requires_explicit_source_window(self):
  d=self.partial_body();d['ledger_lines'][0]['date']='2026-11-08'
  with self.assertRaises(ValueError):body(d,self.context)
if __name__=='__main__':unittest.main()
