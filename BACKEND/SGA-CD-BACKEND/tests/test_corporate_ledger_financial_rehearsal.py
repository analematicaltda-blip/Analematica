"""Corporate authenticated HTTP -> ERP -> durable financial rehearsal, no money."""
import unittest,uuid
import test_corporate_ledger_integration as integration
from app.services import corporate_ledger_commands as commands
class CorporateFinancialRehearsalTests(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 setUp=integration.DualLedgerIntegration.setUp
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def prepare(self):
  company=self.unwrap(self.erp.get(integration.bridge.BASE+'identidad-contable/',params={'provider_id':self.provider}).json())['company_id']
  self.intent={'schema':'sgacd-financial-rehearsal-v1','company_id':company,'request_id':str(uuid.uuid4()),'purpose':'SUPPLIER_PAYMENT','amount':'10.00','currency':'COP','beneficiary_ref':str(uuid.uuid4()),'source_evidence_digest':'a'*64}
  r=self.command('prepare_financial_rehearsal',{'intent':self.intent,'confirmed':True});self.assertEqual(r.status_code,200,r.text);return r.json()['data']
 def test_real_two_confirmations_impact_replay_and_unchanged_ledger(self):
  report=lambda:self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':self.day}).json()['data']
  before=report();p=self.prepare();base={'request_id':p['request_id'],'plan_digest':p['plan_digest'],'confirmed':True}
  phrase='SIMULAR 10.00 COP A '+self.intent['beneficiary_ref']
  self.assertEqual(self.command('simulate_financial_rehearsal',{**base,'impact_confirmation':phrase}).status_code,409)
  for step in (1,2):
   r=self.command('confirm_financial_rehearsal',{**base,'step':step});self.assertEqual(r.status_code,200,r.text)
  self.assertEqual(self.command('simulate_financial_rehearsal',{**base,'impact_confirmation':'SIMULAR 20.00 COP A '+self.intent['beneficiary_ref']}).status_code,409)
  r=self.command('simulate_financial_rehearsal',{**base,'impact_confirmation':phrase});self.assertEqual(r.status_code,200,r.text);d=r.json()['data'];self.assertEqual(d['status'],'SIMULATED_ONLY');self.assertFalse(d['payment_executed']);self.assertFalse(d['desktop_job_created'])
  self.assertTrue(self.command('simulate_financial_rehearsal',{**base,'impact_confirmation':phrase}).json()['data']['replayed']);self.assertEqual(report(),before)
 def test_cancelled_request_and_changed_destination_blocked(self):
  p=self.prepare();base={'request_id':p['request_id'],'plan_digest':p['plan_digest'],'confirmed':True}
  changed={**self.intent,'beneficiary_ref':str(uuid.uuid4())};self.assertEqual(self.command('prepare_financial_rehearsal',{'intent':changed,'confirmed':True}).status_code,409)
  r=self.command('cancel_financial_rehearsal',base);self.assertEqual(r.status_code,200,r.text)
  self.assertEqual(self.command('confirm_financial_rehearsal',{**base,'step':1}).status_code,409)
 def test_no_autoapproval_flag_or_false_confirmation(self):
  p=self.prepare();base={'request_id':p['request_id'],'plan_digest':p['plan_digest'],'step':1,'confirmed':True}
  self.assertEqual(self.command('confirm_financial_rehearsal',{**base,'auto_approve':True}).status_code,422)
  self.assertEqual(self.command('confirm_financial_rehearsal',{**base,'confirmed':False}).status_code,422)
if __name__=='__main__':unittest.main()
