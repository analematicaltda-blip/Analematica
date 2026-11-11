import unittest,copy
import test_corporate_ledger_financial_rehearsal as base
from app.services.financial_rehearsal_contract import validate_state
class RecoveryHTTP(unittest.TestCase):
 login=base.CorporateFinancialRehearsalTests.login
 setUp=base.CorporateFinancialRehearsalTests.setUp
 tearDown=base.CorporateFinancialRehearsalTests.tearDown
 command=base.CorporateFinancialRehearsalTests.command
 prepare=base.CorporateFinancialRehearsalTests.prepare
 def test_state_recovery_then_cancel_and_replay(self):
  p=self.prepare();args={'request_id':p['request_id']};r=self.command('state_financial_rehearsal',args);self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];self.assertEqual(data['intent'],self.intent);self.assertFalse(data['confirmations_restored']);validate_state(data,args,{'tenant_id':data['company_id']})
  for field,value in [('payment_executed',True),('plan_digest','b'*64),('next_step',2),('confirmations_restored',True),('desktop_job_created',True)]:
   bad=copy.deepcopy(data);bad[field]=value
   with self.assertRaises(ValueError):validate_state(bad,args,{'tenant_id':data['company_id']})
  body={**args,'plan_digest':p['plan_digest'],'confirmed':True};self.assertEqual(self.command('cancel_financial_rehearsal',body).status_code,200);self.assertTrue(self.command('cancel_financial_rehearsal',body).json()['data']['replayed']);self.assertEqual(self.command('state_financial_rehearsal',args).json()['data']['status'],'CANCELLED')
 def test_lookup_cannot_override_company_or_use_unknown_reference(self):
  import uuid
  p=self.prepare();self.assertEqual(self.command('state_financial_rehearsal',{'request_id':p['request_id'],'company_id':'foreign'}).status_code,422);self.assertEqual(self.command('state_financial_rehearsal',{'request_id':str(uuid.uuid4())}).status_code,409)
if __name__=='__main__':unittest.main()
