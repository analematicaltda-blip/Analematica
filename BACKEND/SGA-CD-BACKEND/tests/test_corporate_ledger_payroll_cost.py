"""Actual corporate -> HTTP -> ERP cost attribution, disposable data only."""
import os,unittest
from unittest.mock import patch
import test_corporate_ledger_integration as integration
class CorporatePayrollCostTests(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def setUp(self):
  environment=patch.dict(os.environ,{'PAYROLL_BROWSER':'1','OPERATIONAL_COST_FIXTURE':'1'});environment.start();self.addCleanup(environment.stop)
  integration.DualLedgerIntegration.setUp(self)
  p=self.credentials['payroll'];r=self.command('review_payroll',p);self.assertEqual(r.status_code,200,r.text)
  post=self.command('post_payroll',{'payroll_id':p['payroll_id'],'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(post.status_code,200,post.text)
 def result(self,operation,payload):
  r=self.command(operation,payload);self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['cross_database_atomic']);return r.json()['data']
 def test_full_two_confirmation_cost_flow_shared_history_and_report(self):
  p=self.credentials['payroll_cost'];scope={'payroll_id':p['payroll_id']}
  src=self.result('payroll_cost_sources',scope);self.assertEqual(len(src['work']),2);self.assertFalse(src['clinical_content_returned'])
  before=self.result('payroll_cost_state',scope);self.assertIsNone(before['recorded'])
  report_args={'order_id':next(iter(p['operation_centers'])),'since':self.credentials['payroll']['policy']['valid_from'],'until':self.day}
  self.assertIsNone(self.result('operation_labor_costs',report_args)['total_cost'])
  r=self.result('review_payroll_costs',p);self.assertEqual(r['preview']['posted_total_cost'],'600.00');self.assertEqual(r['preview']['unallocated'][0]['total_cost'],'300.00')
  confirm={**scope,'review_id':r['review_id'],'confirmed':False};self.assertEqual(self.command('record_payroll_costs',confirm).status_code,422);confirm['confirmed']=True
  a=self.result('record_payroll_costs',confirm);b=self.result('record_payroll_costs',confirm);self.assertEqual(a['allocation_id'],b['allocation_id']);self.assertTrue(b['replayed']);self.assertFalse(a['ledger_written'])
  state=self.result('payroll_cost_state',scope);self.assertFalse(state['confirmations_restored']);self.assertTrue(state['recorded']['source_current'])
  csrf=self.unwrap(self.erp.get('/api/v1/erp-session/').json())['csrf_token'];direct=self.erp.post(integration.bridge.BASE+'estado-costos-operativos-nomina/',params={'provider_id':self.provider},headers={'X-CSRFToken':csrf},json=scope);self.assertEqual(direct.status_code,200,direct.text);self.assertEqual(state,self.unwrap(direct.json()))
  report=self.result('operation_labor_costs',report_args);self.assertEqual(report['total_cost'],'150.00');self.assertTrue(report['source_complete']);self.assertFalse(report['physical_execution_verified'])
 def test_foreign_source_and_company_override_refused(self):
  import uuid
  p=self.credentials['payroll_cost']
  for operation,payload in [('payroll_cost_sources',{'payroll_id':str(uuid.uuid4())}),('review_payroll_costs',{**p,'provider_id':str(uuid.uuid4())}),('review_payroll_costs',{**p,'confirmed':False})]:
   r=self.command(operation,payload);self.assertIn(r.status_code,(409,422));self.assertNotIn('posted_total_cost',r.text)
  self.login('full-admin_empresa');r=self.command('payroll_cost_sources',{'payroll_id':p['payroll_id']});self.assertEqual(r.status_code,403)
if __name__=='__main__':unittest.main()
