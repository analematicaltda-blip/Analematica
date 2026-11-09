"""Actual corporate/ERP HTTP opening and declared tax-policy flow in disposable stores."""
import os,unittest
from unittest.mock import patch
import test_corporate_ledger_integration as integration
class CorporateRemediationTests(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def setUp(self):
  self.environment_opening=patch.dict(os.environ,{'OPENING_BROWSER':'1'});self.environment_opening.start();self.addCleanup(self.environment_opening.stop)
  integration.DualLedgerIntegration.setUp(self)
 def test_corporate_opening_preserves_source_and_shared_report(self):
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/opening');self.assertEqual(state.status_code,200,state.text);self.assertTrue(state.json()['can_review_first_book'])
  review=self.command('review_opening',{'entry_date':self.day,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True});self.assertEqual(review.status_code,200,review.text)
  body={'review_id':review.json()['data']['review_id'],'confirmed':False};self.assertEqual(self.command('apply_opening',body).status_code,422)
  body['confirmed']=True;posted=self.command('apply_opening',body);self.assertEqual(posted.status_code,200,posted.text)
  self.assertTrue(self.command('apply_opening',body).json()['data']['replayed'])
  report=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':self.day});self.assertEqual(report.status_code,200,report.text);self.assertEqual(report.json()['data']['total_debit'],'100.00')
  state=self.client.get('/api/v1/workspace/corporate/accounting/sources/opening').json();self.assertTrue(state['source_fields_preserved']);self.assertEqual([r['initial_balance'] for r in state['source']],['100.00','100.00'])
 def test_corporate_tax_policy_two_steps_and_exact_readonly_quote(self):
  policy={'code':'CORPORATE_DECLARED','jurisdiction':'CO','currency':'COP','valid_from':self.since,'valid_until':self.until,'rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'DECLARED_TAX','kind':'OUTPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']}]}
  review=self.command('review_tax_policy',{'policy':policy,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True});self.assertEqual(review.status_code,200,review.text)
  recorded=self.command('record_tax_policy',{'review_id':review.json()['data']['review_id'],'confirmed':True});self.assertEqual(recorded.status_code,200,recorded.text);self.assertFalse(recorded.json()['data']['ledger_written'])
  quoted=self.command('quote_tax_policy',{'code':policy['code'],'revision':1,'economic_date':self.day,'net':'100.00','tax_category':'TAXABLE','direction':'SALE'});self.assertEqual(quoted.status_code,200,quoted.text);self.assertEqual(quoted.json()['data']['payable'],'119.00');self.assertFalse(quoted.json()['data']['regulatory_verified'])
  history=self.client.get('/api/v1/workspace/corporate/accounting/sources/tax_policy_history',params={'code':policy['code']});self.assertEqual(history.status_code,200,history.text);self.assertEqual(history.json()['items'][0]['revision'],1)
if __name__=='__main__':unittest.main()
