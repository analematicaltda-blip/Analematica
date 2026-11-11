"""Cost bridge rejects ambiguous financial status and cross-company sources."""
import copy,unittest,uuid
from app.services.payroll_cost_contract import validate
class PayrollCostContractChecks(unittest.TestCase):
 def setUp(self):
  self.context={'tenant_id':str(uuid.uuid4()),'provider_id':str(uuid.uuid4())};self.payroll=str(uuid.uuid4());self.operation=str(uuid.uuid4())
  self.scope={'payroll_id':self.payroll};self.data={'company_id':self.context['tenant_id'],'payroll_id':self.payroll,'allocation_id':str(uuid.uuid4()),'revision':1,'allocation_recorded':True,'ledger_written':False,'money_transferred':False,'confirmations_restored':False,'source_current':True,'replayed':False}
 def test_valid_analytical_record_is_not_a_journal(self):validate('record_payroll_costs',self.data,self.scope,self.context)
 def test_financial_or_restored_authority_rejected(self):
  for change in [{'ledger_written':True},{'money_transferred':True},{'confirmations_restored':True},{'allocation_recorded':False},{'source_current':'true'},{'revision':True}]:
   with self.assertRaises(ValueError):validate('record_payroll_costs',{**self.data,**change},self.scope,self.context)
 def test_foreign_payroll_and_company_rejected(self):
  for key in ['company_id','payroll_id']:
   with self.assertRaises(ValueError):validate('record_payroll_costs',{**self.data,key:str(uuid.uuid4())},self.scope,self.context)
 def report(self):return {'schema':'sgacd-operation-labor-cost-v1','company_id':self.context['tenant_id'],'provider_id':self.context['provider_id'],'operation_id':self.operation,'since':'2026-11-01','until':'2026-11-09','read_only':True,'currency':'COP','date_basis':'PAYROLL_LEDGER_POSTING_DATE','ledger_written':False,'money_transferred':False,'operational_cost_field_overwritten':False,'other_costs_included':False,'physical_execution_verified':False,'source_complete':False,'known_current_cost':'0.00','total_cost':None,'unqualified_allocations':[],'unallocated_payrolls':[self.payroll],'lines':[]}
 def report_payload(self):return {'order_id':self.operation,'since':'2026-11-01','until':'2026-11-09'}
 def test_incomplete_coverage_keeps_null_total(self):validate('operation_labor_costs',self.report(),self.report_payload(),self.context)
 def test_missing_payroll_cannot_be_presented_as_complete(self):
  r=self.report();r.update(source_complete=True,total_cost='0.00')
  with self.assertRaises(ValueError):validate('operation_labor_costs',r,self.report_payload(),self.context)
 def test_incomplete_report_cannot_claim_even_zero_total(self):
  r=self.report();r['total_cost']='0.00'
  with self.assertRaises(ValueError):validate('operation_labor_costs',r,self.report_payload(),self.context)
 def test_money_must_be_exact_string(self):
  for amount in [0,0.0,'NaN','0','-1.00']:
   r=self.report();r['known_current_cost']=amount
   with self.assertRaises(ValueError):validate('operation_labor_costs',r,self.report_payload(),self.context)
 def test_report_scope_and_physical_claims_rejected(self):
  for change in [{'operation_id':str(uuid.uuid4())},{'physical_execution_verified':True},{'since':'2026-10-01'}]:
   with self.assertRaises(ValueError):validate('operation_labor_costs',{**self.report(),**change},self.report_payload(),self.context)
 def test_recovery_never_restores_confirmations(self):
  r={'company_id':self.context['tenant_id'],'payroll_id':self.payroll,'read_only':True,'ledger_written':False,'money_transferred':False,'confirmations_restored':True,'review':None,'recorded':None}
  with self.assertRaises(ValueError):validate('payroll_cost_state',r,self.scope,self.context)
 def test_private_employee_fields_not_allowed(self):
  r={'company_id':self.context['tenant_id'],'provider_id':self.context['provider_id'],'payroll_id':self.payroll,'read_only':True,'payroll_reversed':False,'ledger_written':False,'clinical_content_returned':False,'capacity_inferred':False,'journal_id':str(uuid.uuid4()),'workers':[{'employee_id':str(uuid.uuid4()),'name':'Synthetic','salary':'500.00','employer':'60.00','provisions':'40.00','reviewed_payroll_center':'ONE','medical_record':'PRIVATE'}],'work':[],'operations':[]}
  with self.assertRaises(ValueError):validate('payroll_cost_sources',r,self.scope,self.context)
 def trace_preview(self):
  employee=str(uuid.uuid4());return {'schema':'sgacd-payroll-operation-cost-v2','company_id':self.context['tenant_id'],'provider_id':self.context['provider_id'],'payroll_id':self.payroll,'source_independently_verified':False,'statutory_payroll_rules_verified':False,'journal_id':str(uuid.uuid4()),'payroll_review_id':str(uuid.uuid4()),'payroll_review_digest':'a'*64,'timezone':'America/Bogota','allocation_basis':'OWNER_DECLARED_PAID_CAPACITY_US','rounding':'LARGEST_REMAINDER_UUID_UNALLOCATED_LAST','capacities':[{'employee_id':employee,'capacity_seconds':3600}],'operation_centers':{self.operation:'CENTER'},'operation_sources':[{'operation_id':self.operation,'commercial_reference_id':str(uuid.uuid4()),'planned_start':'2026-11-01T09:00:00-05:00','planned_end':'2026-11-01T10:00:00-05:00','description_digest':'b'*64,'active':True}],'work_source':[],'allocations':[{'employee_id':employee,'operation_id':self.operation,'center_code':'CENTER','allocation_weight_us':3600000000,'amounts':{'salary':'10.00','employer':'0.00','provisions':'0.00'},'total_cost':'10.00'}],'unallocated':[],'posted_cost':{'salary':'10.00','employer':'0.00','provisions':'0.00'},'posted_total_cost':'10.00'}
 def test_v2_trace_preview_is_accepted(self):
  from app.services.payroll_cost_contract import preview
  preview(self.trace_preview(),self.payroll,self.context)
 def test_v2_missing_duplicate_or_foreign_trace_rejected(self):
  from app.services.payroll_cost_contract import preview
  for case in ['missing','duplicate','foreign','private','naive']:
   p=self.trace_preview()
   if case=='missing':p['operation_sources']=[]
   if case=='duplicate':p['operation_sources']*=2
   if case=='foreign':p['operation_sources'][0]['operation_id']=str(uuid.uuid4())
   if case=='private':p['operation_sources'][0]['medical_record']='secret'
   if case=='naive':p['operation_sources'][0]['planned_start']='2026-11-01T09:00:00'
   with self.assertRaises(ValueError):preview(p,self.payroll,self.context)
if __name__=='__main__':unittest.main()
