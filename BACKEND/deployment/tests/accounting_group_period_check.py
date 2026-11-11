"""Grouped associations and complete-period coverage stay separate and exact."""
import runpy,unittest,uuid,copy
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_bank_grouped_check.py')),run_name='group_period_fixture')
from apps.core_erp.accounting import bank_grouped as engine
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
class GroupPeriodChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['GroupedBankChecks']();self.base.setUp();self.case=self.base.case
  self.period={'since':self.base.base.bank.day,'until':self.base.base.bank.day,'opening':'0.00','closing':'10.00','statement_complete':True,'evidence_digest':'f'*64}
 def review(self,**kw):return self.base.review(**{'period':self.period,**kw})
 def post_cash(self,opposite=False):return LedgerEngine.post_lines(tenant_id=self.case.tenant.pk,entry_date=self.base.base.bank.entry.date,description='Synthetic omitted grouped cash',actor=self.case.user,idempotency_key=str(uuid.uuid4()),lines_data=[{'account':self.case.b if opposite else self.case.a,'debit':'3.00'},{'account':self.case.a if opposite else self.case.b,'credit':'3.00'}])
 def test_complete_grouped_period_requires_second_confirmation(self):
  before=self.base.base.counts();r=self.review();self.assertTrue(r['preview']['period_assessment']['eligible_for_period_reconciliation']);a=self.base.confirm(r);self.assertTrue(a['groups_confirmed']);self.assertTrue(a['period_reconciled']);self.assertTrue(a['period_source_current']);self.assertEqual(before,self.base.base.counts());self.assertFalse(a['bank_verified']);self.assertEqual(a['reconciliation_id'],self.base.confirm(r)['reconciliation_id']);self.assertTrue(self.base.confirm(r)['replayed'])
 def test_omitted_offsetting_movements_cannot_hide_in_balanced_totals(self):
  self.post_cash();self.post_cash(True);a=self.base.confirm(self.review());self.assertTrue(a['groups_confirmed']);self.assertTrue(a['period_assessment']['balances_match']);self.assertEqual(len(a['period_assessment']['unmatched_ledger_line_ids']),2);self.assertFalse(a['period_reconciled'])
 def test_wrong_declared_opening_does_not_qualify_grouped_period(self):
  a=self.base.confirm(self.review(period={**self.period,'opening':'1.00','closing':'11.00'}));self.assertFalse(a['period_reconciled']);self.assertEqual(a['period_assessment']['opening_difference'],'1.00')
 def test_bank_arithmetic_and_explicit_complete_declaration_required(self):
  for terms in [{**self.period,'closing':'11.00'},{**self.period,'statement_complete':False}]:
   with self.assertRaises(AccountingError):self.review(period=terms)
 def test_new_movement_between_confirmations_blocks_all_claims(self):
  r=self.review();self.post_cash();before=OutboxEvent.objects.filter(event_type=engine.APPLIED).count()
  with self.assertRaises(AccountingError):self.base.confirm(r)
  self.assertEqual(before,OutboxEvent.objects.filter(event_type=engine.APPLIED).count())
 def test_posting_after_confirmation_invalidates_period_not_historical_groups(self):
  r=self.review();self.base.confirm(r);self.post_cash();a=self.base.confirm(r);self.assertTrue(a['groups_confirmed']);self.assertFalse(a['period_source_current']);self.assertFalse(a['period_reconciled']);state=engine.state(self.case.tenant.pk,actor=self.case.user,account_id=str(self.case.a.pk),source_digest=r['preview']['source_digest']);self.assertFalse(state['applied']['period_reconciled'])
 def test_release_removes_period_qualification_and_keeps_assessment(self):
  a=self.base.confirm(self.review());released=self.base.release(a);self.assertTrue(released['released']);self.assertFalse(released['period_reconciled']);self.assertIsNotNone(released['period_assessment'])
 def test_partial_allocation_never_means_full_cash_line_coverage(self):
  csv=self.base.csv.splitlines()[0]+'\npartial,'+self.period['since']+',IN,6.00,COP\n'
  groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1],'ledger_allocations':[{'ledger_line_id':self.base.line,'amount':'6.00'}]}]
  a=self.base.confirm(self.review(csv_text=csv,groups=groups,period={**self.period,'closing':'6.00'}));self.assertTrue(a['groups_confirmed']);self.assertFalse(a['period_assessment']['group_allocations_complete']);self.assertFalse(a['period_reconciled'])
 def test_complete_partial_mode_allocations_may_qualify(self):
  groups=[{'group_id':str(uuid.uuid4()),'bank_rows':[1,2],'ledger_allocations':[{'ledger_line_id':self.base.line,'amount':'10.00'}]}]
  a=self.base.confirm(self.review(groups=groups));self.assertTrue(a['period_assessment']['group_allocations_complete']);self.assertTrue(a['period_reconciled'])
 def test_inactive_account_invalidates_confirmed_period_without_losing_history(self):
  from apps.core_erp.accounting.models import Account
  r=self.review();self.base.confirm(r);Account.plain_objects.filter(pk=self.case.a.pk).update(is_active=False)
  a=self.base.confirm(r);self.assertFalse(a['period_reconciled']);self.assertFalse(a['period_source_current']);self.assertTrue(a['period_requires_review'])
 def test_no_optional_period_keeps_existing_contract(self):
  a=self.base.confirm(self.base.review());self.assertIsNone(a['period_assessment']);self.assertIsNone(a['period_source_current']);self.assertFalse(a['period_reconciled'])
 def test_erp_period_and_corporate_contract(self):
  payload={**{k:v for k,v in self.base.args.items() if k!='actor'},'groups':self.base.groups,'period':self.period,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True}
  r=self.case.call('review_bank_groups','post',payload);self.assertEqual(r.status_code,200,r.data);args={'statement_id':r.data['statement_id'],'review_id':r.data['review_id'],'confirmed':True};a=self.case.call('confirm_bank_groups','post',args);self.assertEqual(a.status_code,200,a.data)
  validate=runpy.run_path(str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND/app/services/bank_group_contract.py'))['validate'];ctx={'tenant_id':str(self.case.tenant.pk)};validate('review_bank_groups',r.data,payload,ctx);validate('confirm_bank_groups',a.data,args,ctx)
  broken=copy.deepcopy(a.data);broken['period_assessment']['group_allocations_complete']=False
  with self.assertRaises(ValueError):validate('confirm_bank_groups',broken,args,ctx)
  broken=copy.deepcopy(a.data);broken['period_source_current']=False
  with self.assertRaises(ValueError):validate('confirm_bank_groups',broken,args,ctx)
if __name__=='__main__':unittest.main()
