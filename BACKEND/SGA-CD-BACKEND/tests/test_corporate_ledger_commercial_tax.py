"""Authenticated corporate -> ERP -> reviewed purchase/input tax/withholding ledger."""
import unittest,uuid
import test_corporate_ledger_integration as integration
class CorporateCommercialTaxChecks(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 setUp=integration.DualLedgerIntegration.setUp
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 def prepare(self):
  session=self.unwrap(self.erp.get('/api/v1/erp-session/').json());headers={'X-CSRFToken':session['csrf_token'],'Origin':self.origin,'Referer':self.origin+'/'};ids={}
  for role,code in [('basis','510070'),('input','135570'),('withholding','236570'),('payable','220570')]:
   r=self.erp.post(integration.bridge.BASE,params={'provider_id':self.provider},headers=headers,json={'code':code,'name':'Synthetic tax70 '+role});self.assertEqual(r.status_code,201,r.text);ids[role]=self.unwrap(r.json())['id']
  policy={'code':'CORPORATE_PURCHASE70','jurisdiction':'CO','currency':'COP','valid_from':self.day[:4]+'-01-01','valid_until':self.day[:4]+'-12-31','rounding':'PER_COMPONENT_HALF_UP','components':[{'code':'INPUT','kind':'INPUT_TAX','rate_bps':1900,'applies_to':['TAXABLE']},{'code':'RET','kind':'WITHHOLDING','rate_bps':250,'applies_to':['TAXABLE']}]}
  r=self.command('review_tax_policy',{'policy':policy,'evidence_digest':'a'*64,'expected_revision':0,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('record_tax_policy',{'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  return {'document_id':str(uuid.uuid4()),'document_digest':uuid.uuid4().hex*2,'counterparty_id':str(uuid.uuid4()),'direction':'PURCHASE','entry_date':self.day,'settlement_account_id':ids['payable'],'items':[{'item_id':str(uuid.uuid4()),'net':'100.00','tax_category':'TAXABLE','policy_code':policy['code'],'policy_revision':1,'basis_account_id':ids['basis'],'tax_accounts':{'INPUT':ids['input'],'RET':ids['withholding']}}]}
 def test_purchase_real_http_post_replay_and_state(self):
  fact=self.prepare();r=self.command('review_commercial_tax',{'fact':fact,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True});self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['preview']['totals']['settlement'],'116.50')
  payload={'document_id':fact['document_id'],'review_id':r.json()['data']['review_id'],'confirmed':True};r=self.command('post_commercial_tax',payload);self.assertEqual(r.status_code,200,r.text);journal=r.json()['data']['journal_id'];self.assertFalse(r.json()['data']['money_transferred']);self.assertFalse(r.json()['data']['regulatory_verified'])
  r=self.command('post_commercial_tax',payload);self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['journal_id'],journal);self.assertTrue(r.json()['data']['replayed'])
  r=self.command('commercial_tax_state',{'document_id':fact['document_id']});self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['posted']['journal_id'],journal)
  r=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'tax_register','since':self.day,'until':self.day,'account_id':fact['items'][0]['tax_accounts']['INPUT']});self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['tax_by_kind']['INPUT_TAX'],'19.00');self.assertEqual(r.json()['data']['unattributed_normal_movement'],'0.00')
  r=self.command('review_commercial_tax_reversal',{'document_id':fact['document_id'],'reason_code':'CORRECTION','evidence_digest':'c'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  rev={'document_id':fact['document_id'],'review_id':r.json()['data']['review_id'],'confirmed':True};r=self.command('reverse_commercial_tax',rev);self.assertEqual(r.status_code,200,r.text);contra=r.json()['data']['journal_id'];self.assertNotEqual(contra,journal)
  r=self.command('reverse_commercial_tax',rev);self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['data']['replayed']);self.assertEqual(r.json()['data']['journal_id'],contra)
  r=self.command('commercial_tax_state',{'document_id':fact['document_id']});self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['data']['posted']['reversed'])
 def test_corporate_cannot_override_company_or_skip_confirmation(self):
  fact=self.prepare();payload={'fact':fact,'evidence_digest':'b'*64,'expected_revision':0,'confirmed':True}
  self.assertEqual(self.command('review_commercial_tax',{**payload,'provider_id':str(uuid.uuid4())}).status_code,422)
  self.assertEqual(self.command('review_commercial_tax',{**payload,'confirmed':False}).status_code,422)
if __name__=='__main__':unittest.main()
