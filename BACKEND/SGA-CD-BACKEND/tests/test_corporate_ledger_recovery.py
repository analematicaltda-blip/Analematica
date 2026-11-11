"""Real corporate HTTP recovery commands with disposable ERP and corporate DBs."""
import unittest,uuid
import test_corporate_ledger_native_purchase as native
import test_corporate_ledger_integration as integration
class CorporateRecoveryChecks(native.CorporateNativePurchaseChecks):
 # Use existing setup/capture helpers but keep this suite focused on recovery.
 def test_native_invoice_http_review_post_recovery_tax_and_reversal(self):
  fact,capture=self.capture();invoice=capture['invoice_id']
  r=self.command('review_purchase_correction',{'invoice_id':invoice,'request_id':str(uuid.uuid4()),'changes':{'notes':'Synthetic corrected support'},'evidence_digest':'d'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('confirm_purchase_correction',{'invoice_id':invoice,'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('purchase_history',{'invoice_id':invoice});self.assertEqual(r.status_code,200,r.text);self.assertEqual(len(r.json()['data']['corrections']),1)
  r=self.command('review_native_purchase',{'invoice_id':invoice,'selection':fact['items'],'settlement_account_id':fact['settlement_account_id'],'economic_fact':'GOODS_OR_SERVICES_RECEIVED','evidence_digest':'c'*64,'expected_revision':0,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('post_native_purchase',{'invoice_id':invoice,'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('review_purchase_return',{'invoice_id':invoice,'request_id':str(uuid.uuid4()),'return_bps':4000,'economic_date':self.day,'reason_code':'PARTIAL_RETURN','evidence_digest':'e'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  args={'invoice_id':invoice,'review_id':r.json()['data']['review_id'],'confirmed':True};r=self.command('confirm_purchase_return',args);self.assertEqual(r.status_code,200,r.text);journal=r.json()['data']['journal_id']
  r=self.command('confirm_purchase_return',args);self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['data']['journal_id'],journal);self.assertTrue(r.json()['data']['replayed'])
  for component,kind,total in [('INPUT','INPUT_TAX','11.40'),('RET','WITHHOLDING','1.50')]:
   report=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'tax_register','account_id':fact['items'][0]['tax_accounts'][component],'since':self.day,'until':self.day});self.assertEqual(report.status_code,200,report.text);data=report.json()['data'];self.assertEqual(data['tax_by_kind'][kind],total);self.assertEqual(data['unattributed_normal_movement'],'0.00');self.assertFalse(data['dian_compared']);self.assertFalse(data['fiscal_accepted'])

 def test_esg_draft_real_http_preserves_source_and_correction(self):
  factor={'id':'fixture-http-factor','version':'declared-v1','unit':'vehicle_km','kg_co2e_per_unit':'0.2','valid_from':self.day[:4]+'-01-01','valid_until':self.day[:4]+'-12-31','source_digest':'a'*64,'geography':'CO','boundary':'direct_combustion'}
  activity={'id':'http-observation','date':self.day,'quantity':'100','unit':'vehicle_km','factor_id':factor['id'],'passengers':None}
  r=self.command('review_environmental',{'activities':[activity],'factors':[factor],'evidence_digest':'b'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('record_environmental',{'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  mapping={'framework':'SASB','version':'declared-v1','disclosure':'declared-metric','boundary':'direct_combustion','applicability_reason':'Synthetic scoped mapping only','evidence_digest':'c'*64}
  r=self.command('esg_report',{'since':self.day,'until':self.day,'mappings':[mapping]});self.assertEqual(r.status_code,200,r.text);data=r.json()['data'];self.assertEqual(data['disclosures'][0]['value'],'20.000000');self.assertFalse(data['esg_certified']);self.assertIn('no-store',r.headers['cache-control'])
 def test_grouped_partial_bank_http_recovery_and_release(self):
  import test_corporate_ledger_bank as bank
  account,text=bank.CorporateBankTests.bank_source(self)
  compared=self.command('compare_bank_statement',{'account_id':account,'csv_text':text});self.assertEqual(compared.status_code,200,compared.text);line=compared.json()['data']['rows'][0]['candidates'][0]['ledger_line_id']
  text=text.replace('10.00','4.00')
  payload={'account_id':account,'csv_text':text,'groups':[{'rows':[1],'ledger_line_ids':[line],'ledger_allocations':{line:'4.00'},'remainder_reason':'TIMING_DIFFERENCE'}],'differences':[],'evidence_digest':'a'*64,'confirmed':True}
  r=self.command('review_bank_groups',payload);self.assertEqual(r.status_code,200,r.text);review=r.json()['data']['review_id']
  r=self.command('confirm_bank_groups',{'review_id':review,'confirmed':True});self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['data']['fully_reconciled']);self.assertEqual(r.json()['data']['ledger_remainders'][0]['amount'],'6.00')
  r=self.command('bank_group_state',{'review_id':review});self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['data']['confirmations_restored'])
  r=self.command('review_bank_group_release',{'review_id':review,'reason_code':'WRONG_MATCH','evidence_digest':'b'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text)
  r=self.command('confirm_bank_group_release',{'review_id':r.json()['data']['review_id'],'confirmed':True});self.assertEqual(r.status_code,200,r.text);self.assertTrue(r.json()['data']['released'])
if __name__=='__main__' :unittest.main()
