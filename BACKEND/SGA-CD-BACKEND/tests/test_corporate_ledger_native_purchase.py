"""Actual HTTP native invoice intake, protected source, canonical accrual and reversal."""
import unittest,uuid,os
from unittest.mock import patch
import test_corporate_ledger_integration as integration
import test_corporate_ledger_commercial_tax as commercial
class CorporateNativePurchaseChecks(unittest.TestCase):
 login=integration.DualLedgerIntegration.login
 tearDown=integration.DualLedgerIntegration.tearDown
 command=integration.DualLedgerIntegration.command
 prepare=commercial.CorporateCommercialTaxChecks.prepare
 def setUp(self):
  env=patch.dict(os.environ,{'NATIVE_PURCHASE_FIXTURE':'1'});env.start();self.addCleanup(env.stop);integration.DualLedgerIntegration.setUp(self)
 def capture(self):
  fact=self.prepare()
  r=self.command('record_native_supplier',{'request_id':str(uuid.uuid4()),'name':'Synthetic native supplier HTTP','identification':'SYNTHETIC-HTTP','evidence_digest':'a'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text);supplier=r.json()['data']['supplier_id']
  r=self.command('record_native_purchase',{'request_id':str(uuid.uuid4()),'supplier_id':supplier,'number':'SYNTHETIC-HTTP-001','issue_date':self.day,'due_date':None,'subtotal':'100.00','tax':'19.00','gross':'119.00','document_digest':uuid.uuid4().hex*2,'evidence_digest':'b'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  return fact,r.json()['data']
 def test_native_invoice_http_review_post_recovery_tax_and_reversal(self):
  fact,capture=self.capture();invoice=capture['invoice_id'];self.assertFalse(capture['ledger_written'])
  body={'invoice_id':invoice,'selection':fact['items'],'settlement_account_id':fact['settlement_account_id'],'economic_fact':'GOODS_OR_SERVICES_RECEIVED','evidence_digest':'c'*64,'expected_revision':0,'confirmed':True}
  r=self.command('review_native_purchase',body);self.assertEqual(r.status_code,200,r.text);review=r.json()['data'];self.assertTrue(review['native_source_verified'])
  generic={'document_id':capture['document_id'],'review_id':review['review_id'],'confirmed':True};self.assertEqual(self.command('post_commercial_tax',generic).status_code,409)
  args={'invoice_id':invoice,'review_id':review['review_id'],'confirmed':True};r=self.command('post_native_purchase',args);self.assertEqual(r.status_code,200,r.text);journal=r.json()['data']['journal_id']
  r=self.command('post_native_purchase',args);self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['data']['replayed']);self.assertEqual(r.json()['data']['journal_id'],journal)
  r=self.command('native_purchase_state',{'invoice_id':invoice});self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['data']['confirmations_restored']);self.assertEqual(r.json()['data']['posted']['journal_id'],journal)
  r=self.command('native_purchase_sources',{'after_id':None});self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['invoices'][0]['invoice_id'],invoice)
  r=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'tax_register','account_id':fact['items'][0]['tax_accounts']['INPUT'],'since':self.day,'until':self.day});self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['tax_by_kind']['INPUT_TAX'],'19.00')
  r=self.command('review_native_purchase_reversal',{'invoice_id':invoice,'reason_code':'CORRECTION','evidence_digest':'d'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  reverse={'invoice_id':invoice,'review_id':r.json()['data']['review_id'],'confirmed':True};r=self.command('reverse_native_purchase',reverse);self.assertEqual(r.status_code,200,r.text);self.assertNotEqual(r.json()['data']['journal_id'],journal);r=self.command('reverse_native_purchase',reverse);self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['data']['replayed'])
 def test_native_partial_return_post_state_tax_and_idempotency(self):
  fact,capture=self.capture();invoice=capture['invoice_id'];r=self.command('review_native_purchase',{'invoice_id':invoice,'selection':fact['items'],'settlement_account_id':fact['settlement_account_id'],'economic_fact':'GOODS_OR_SERVICES_RECEIVED','evidence_digest':'c'*64,'expected_revision':0,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('post_native_purchase',{'invoice_id':invoice,'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text);original=r.json()['data']['journal_id']
  state=self.command('purchase_return_state',{'invoice_id':invoice});self.assertEqual(state.status_code,200,state.text);self.assertEqual(state.json()['data']['remaining']['net'],'100.00')
  args={'invoice_id':invoice,'return_id':str(uuid.uuid4()),'net_amount':'25.00','entry_date':self.day,'document_digest':uuid.uuid4().hex*2,'evidence_digest':'d'*64,'expected_revision':0,'confirmed':True};r=self.command('review_purchase_return',args);self.assertEqual(r.status_code,200,r.text);review=r.json()['data'];self.assertEqual(review['preview']['totals']['tax'],'4.75')
  payload={'invoice_id':invoice,'review_id':review['review_id'],'confirmed':True};self.assertEqual(self.command('post_purchase_return',{**payload,'confirmed':False}).status_code,422);r=self.command('post_purchase_return',payload);self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['remaining']['net'],'75.00');self.assertTrue(self.command('post_purchase_return',payload).json()['data']['replayed']);self.assertFalse(r.json()['data']['money_transferred']);self.assertNotEqual(r.json()['data']['journal_id'],original)
  r=self.command('purchase_return_state',{'invoice_id':invoice});self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['data']['confirmations_restored'])
  tax=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'tax_register','account_id':fact['items'][0]['tax_accounts']['INPUT'],'since':self.day,'until':self.day});self.assertEqual(tax.status_code,200,tax.text);self.assertEqual(tax.json()['data']['tax_by_kind']['INPUT_TAX'],'14.25')
  correction={'invoice_id':invoice,'return_id':args['return_id'],'request_id':str(uuid.uuid4()),'entry_date':self.day,'reason_code':'DATA_ENTRY_ERROR','evidence_digest':'e'*64,'expected_revision':1,'confirmed':True};r=self.command('review_purchase_return_void',correction);self.assertEqual(r.status_code,200,r.text)
  confirm={'invoice_id':invoice,'review_id':r.json()['data']['review_id'],'confirmed':True};self.assertEqual(self.command('void_purchase_return',{**confirm,'confirmed':False}).status_code,422);r=self.command('void_purchase_return',confirm);self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['remaining']['net'],'100.00');self.assertTrue(r.json()['data']['returns'][0]['reversed']);self.assertTrue(self.command('void_purchase_return',confirm).json()['data']['replayed'])
  r=self.command('purchase_return_state',{'invoice_id':invoice});self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['data']['confirmations_restored']);self.assertEqual(r.json()['data']['returned']['net'],'0.00')
  tax=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'tax_register','account_id':fact['items'][0]['tax_accounts']['INPUT'],'since':self.day,'until':self.day});self.assertEqual(tax.status_code,200,tax.text);self.assertEqual(tax.json()['data']['tax_by_kind']['INPUT_TAX'],'19.00')
  r=self.command('review_native_purchase_reversal',{'invoice_id':invoice,'reason_code':'CORRECTION','evidence_digest':'f'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  final={'invoice_id':invoice,'review_id':r.json()['data']['review_id'],'confirmed':True};self.assertEqual(self.command('reverse_native_purchase',{**final,'confirmed':False}).status_code,422);r=self.command('reverse_native_purchase',final);self.assertEqual(r.status_code,200,r.text);self.assertTrue(self.command('reverse_native_purchase',final).json()['data']['replayed'])
  r=self.command('purchase_return_state',{'invoice_id':invoice});self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['data']['original_reversed']);self.assertEqual(r.json()['data']['remaining']['net'],'0.00')
  tax=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'tax_register','account_id':fact['items'][0]['tax_accounts']['INPUT'],'since':self.day,'until':self.day});self.assertEqual(tax.status_code,200,tax.text);self.assertEqual(tax.json()['data']['tax_by_kind']['INPUT_TAX'],'0.00')


 def test_history_is_authenticated_read_only_and_keeps_current_phase(self):
  fact,capture=self.capture();payload={'after_id':None,'search':'SYNTHETIC-HTTP'}
  r=self.command('native_purchase_history',payload);self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];self.assertEqual(data['invoices'][0]['invoice_id'],capture['invoice_id']);self.assertEqual(data['invoices'][0]['accounting_phase'],'CAPTURED');self.assertFalse(data['ledger_written']);self.assertFalse(data['confirmations_restored'])
  r=self.command('native_purchase_history',{'after_id':None,'search':'NOT-FOUND'});self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['invoices'],[])
  self.assertEqual(self.command('native_purchase_history',{**payload,'company_id':str(uuid.uuid4())}).status_code,422)
 def test_native_contract_rejects_context_override_and_missing_approval(self):
  body={'request_id':str(uuid.uuid4()),'name':'Synthetic supplier','identification':'SYNTHETIC-HTTP','evidence_digest':'a'*64,'confirmed':True}
  self.assertEqual(self.command('record_native_supplier',{**body,'provider_id':str(uuid.uuid4())}).status_code,422)
  self.assertEqual(self.command('record_native_supplier',{**body,'confirmed':False}).status_code,422)
  r=self.command('native_purchase_state',{'invoice_id':99999999});self.assertEqual(r.status_code,409)
if __name__=='__main__':unittest.main()
