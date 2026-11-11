"""Actual authenticated corporate HTTP -> ERP policy -> reservation -> journal."""
import unittest,uuid
import test_corporate_ledger_integration as integration
class CorporateReservationPolicyChecks(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 setUp=integration.DualLedgerIntegration.setUp
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def record_policy(self,withholding=False):
  policy={'code':'CORPORATE_POLICY68','jurisdiction':'CO','currency':'COP','valid_from':self.day[:4]+'-01-01','valid_until':self.day[:4]+'-12-31','rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'DECLARED_OUTPUT','kind':'OUTPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']}]}
  if withholding:policy['components'].append({'code':'DECLARED_RET','kind':'WITHHOLDING','rate_bps':250,'applies_to':['TAXABLE']})
  r=self.command('review_tax_policy',{'policy':policy,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('record_tax_policy',{'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  return {'reservation_id':self.credentials['reservation_id'],'selection':[{'item_id':str(uuid.uuid4()),'net':'84.03','tax_category':'TAXABLE','policy_code':policy['code'],'policy_revision':1}],'economic_date':self.day,'evidence_digest':'b'*64,'confirmed':True,'expected_revision':0}
 def test_actual_policy_tax_posting_and_same_journal_recovery(self):
  args=self.record_policy();r=self.command('review_reservation_policy',args);self.assertEqual(r.status_code,200,r.text);fiscal=r.json()['data'];self.assertEqual(fiscal['preview']['quotes'][0]['quote']['output_tax'],'15.97');self.assertFalse(fiscal['fiscal_accepted'])
  session=self.unwrap(self.erp.get('/api/v1/erp-session/').json());created=self.erp.post(integration.bridge.BASE,params={'provider_id':self.provider},headers={'X-CSRFToken':session['csrf_token'],'Origin':self.origin,'Referer':self.origin+'/'},json={'code':'240505','name':'Synthetic reviewed tax liability'})
  self.assertEqual(created.status_code,201,created.text);tax=self.unwrap(created.json())['id']
  payload={'reservation_id':self.credentials['reservation_id'],'fiscal_review_id':fiscal['review_id'],'entry_date':self.day,'account_mapping':{'receivable':self.credentials['recognition_receivable_id'],'revenue':self.credentials['recognition_revenue_id'],'tax_liability':tax},'service_evidence_digest':'c'*64,'policy_evidence_digest':'d'*64,'economic_fact':'SERVICE_DELIVERED','confirmed':True,'expected_revision':0}
  r=self.command('review_recognition',payload);self.assertEqual(r.status_code,200,r.text);review=r.json()['data']
  body={'reservation_id':self.credentials['reservation_id'],'review_id':review['review_id'],'confirmed':True};posted=self.command('post_recognition',body);self.assertEqual(posted.status_code,200,posted.text);result=posted.json()['data'];self.assertTrue(result['ledger_written']);self.assertFalse(result['fiscal_accepted']);self.assertFalse(result['money_transferred'])
  again=self.command('post_recognition',body);self.assertEqual(again.status_code,200,again.text);self.assertTrue(again.json()['data']['replayed']);self.assertEqual(result['journal_id'],again.json()['data']['journal_id'])
  report=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':self.day});self.assertEqual(report.status_code,200,report.text);self.assertEqual(report.json()['data']['total_debit'],report.json()['data']['total_credit'])
 def test_reviewed_ubl_source_over_authenticated_http(self):
  args=self.record_policy();review=self.command('review_reservation_policy',args);self.assertEqual(review.status_code,200,review.text)
  params={'reservation_id':self.credentials['reservation_id'],'review_id':review.json()['data']['review_id']}
  path='/api/v1/workspace/corporate/accounting/sources/ubl_source'
  response=self.client.get(path,params=params);self.assertEqual(response.status_code,200,response.text)
  source=response.json();self.assertEqual(source['snapshot']['totals']['gross'],'100.00');self.assertEqual(source['snapshot']['items'][0]['tax'],'15.97');self.assertFalse(source['fiscal_accepted']);self.assertTrue(source['read_only'])
  self.assertEqual(self.client.get(path,params={**params,'company_id':str(uuid.uuid4())}).status_code,422)
  self.assertEqual(self.client.get(path,params={'reservation_id':params['reservation_id']}).status_code,422)
  second=self.command('review_reservation_policy',{**args,'expected_revision':1});self.assertEqual(second.status_code,200,second.text)
  self.assertNotEqual(self.client.get(path,params=params).status_code,200)
 def test_withholding_missing_version_and_company_override_blocked(self):
  args=self.record_policy(withholding=True);self.assertEqual(self.command('review_reservation_policy',args).status_code,409)
  self.assertEqual(self.command('review_reservation_policy',{**args,'provider_id':str(uuid.uuid4())}).status_code,422)
  args['selection'][0]['policy_revision']=999;self.assertEqual(self.command('review_reservation_policy',args).status_code,409)
if __name__=='__main__':unittest.main()
