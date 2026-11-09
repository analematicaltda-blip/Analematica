"""Actual corporate -> HTTP -> ERP declared-payroll accrual, synthetic stores."""
import os,unittest
from unittest.mock import patch
import test_corporate_ledger_integration as integration
class CorporatePayrollTests(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def setUp(self):
  environment=patch.dict(os.environ,{'PAYROLL_BROWSER':'1'});environment.start();self.addCleanup(environment.stop)
  integration.DualLedgerIntegration.setUp(self)
 def test_two_confirmations_shared_journal_and_recovery_through_both_apis(self):
  payload=self.credentials['payroll'];review=self.command('review_payroll',payload);self.assertEqual(review.status_code,200,review.text)
  self.assertFalse(review.json()['data']['ledger_written']);self.assertEqual(review.json()['data']['preview']['snapshot']['totals']['net'],'480.00')
  args={'payroll_id':payload['payroll_id'],'review_id':review.json()['data']['review_id'],'confirmed':False};self.assertEqual(self.command('post_payroll',args).status_code,422)
  args['confirmed']=True;posted=self.command('post_payroll',args);self.assertEqual(posted.status_code,200,posted.text);self.assertFalse(posted.json()['data']['money_transferred'])
  replay=self.command('post_payroll',args);self.assertEqual(replay.status_code,200,replay.text);self.assertTrue(replay.json()['data']['replayed']);self.assertEqual(replay.json()['data']['journal_id'],posted.json()['data']['journal_id'])
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/payroll_status',params={'payroll_id':payload['payroll_id']});self.assertEqual(state.status_code,200,state.text);self.assertFalse(state.json()['confirmations_restored'])
  direct=self.unwrap(self.erp.get(integration.bridge.BASE+'estado-nomina-revisada/',params={'provider_id':self.provider,'payroll_id':payload['payroll_id']}).json());self.assertEqual(state.json(),direct)
  report=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':self.day});self.assertEqual(report.status_code,200,report.text);self.assertEqual(report.json()['data']['total_debit'],'615.00');self.assertEqual(report.json()['data']['total_credit'],'615.00')
 def test_declared_overtime_and_surcharge_post_and_recover_through_bridge(self):
  import copy
  payload=copy.deepcopy(self.credentials['payroll']);payload['policy']['earning_rules']=[{'code':'EXTRA','kind':'OVERTIME','rate_bps':12500,'hour_divisor':200},{'code':'NIGHT','kind':'SURCHARGE','rate_bps':3500,'hour_divisor':200}]
  for rule in payload['policy']['components']:rule['basis']='GROSS'
  payload['workers'][0]['earnings']=[{'code':'EXTRA','minutes':120,'evidence_digest':'c'*64},{'code':'NIGHT','minutes':60,'evidence_digest':'d'*64}]
  r=self.command('review_payroll',payload);self.assertEqual(r.status_code,200,r.text);s=r.json()['data']['preview']['snapshot'];self.assertEqual(s['totals']['gross'],'514.25');self.assertEqual(s['workers'][0]['earning_totals'],{'horas_extras':'12.50','recargos':'1.75'})
  p=self.command('post_payroll',{'payroll_id':payload['payroll_id'],'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(p.status_code,200,p.text);self.assertFalse(p.json()['data']['money_transferred'])
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/payroll_status',params={'payroll_id':payload['payroll_id']});self.assertEqual(state.status_code,200,state.text);self.assertEqual(state.json()['preview']['snapshot']['totals']['net'],'493.68');self.assertEqual(state.json()['applied']['details_projection'],'DECLARED_EARNINGS_TOTALS')
if __name__=='__main__':unittest.main()
