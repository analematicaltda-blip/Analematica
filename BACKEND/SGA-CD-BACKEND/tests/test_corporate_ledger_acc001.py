"""ACC001: real native purchase intake and posting through both authenticated APIs."""
import unittest,uuid
import test_corporate_ledger_integration as integration
import test_corporate_ledger_native_purchase as native
class ACC001HTTP(unittest.TestCase):
 setUp=native.CorporateNativePurchaseChecks.setUp
 tearDown=native.CorporateNativePurchaseChecks.tearDown
 login=native.CorporateNativePurchaseChecks.login
 command=integration.DualLedgerIntegration.command
 prepare=native.CorporateNativePurchaseChecks.prepare
 capture=native.CorporateNativePurchaseChecks.capture
 prepare_recognition=integration.DualLedgerIntegration.prepare_recognition
 def direct(self,path,body):
  session=self.unwrap(self.erp.get('/api/v1/erp-session/').json());return self.erp.post(integration.bridge.BASE+path+'/',params={'provider_id':self.provider},headers={'X-CSRFToken':session['csrf_token'],'Origin':self.origin,'Referer':self.origin+'/'},json=body)
 def test_invalid_money_rejected_by_both_entry_points_without_persisted_invoice(self):
  r=self.command('record_native_supplier',{'request_id':str(uuid.uuid4()),'name':'ACC001 synthetic','identification':'ACC001-SYNTHETIC','evidence_digest':'a'*64,'confirmed':True});self.assertEqual(r.status_code,200,r.text);supplier=r.json()['data']['supplier_id']
  for amount in [1.0,True,'NaN','Infinity','0.001','10000000000000000']:
   body={'request_id':str(uuid.uuid4()),'supplier_id':supplier,'number':'ACC001-'+uuid.uuid4().hex,'issue_date':self.day,'due_date':None,'subtotal':amount,'tax':'19.00','gross':'119.00','document_digest':'e'*64,'evidence_digest':'b'*64,'confirmed':True}
   self.assertIn(self.direct('registrar-factura-compra-nativa',body).status_code,[400,409,422]);self.assertIn(self.command('record_native_purchase',body).status_code,[400,409,422])
  response=self.command('native_purchase_sources',{'after_id':None});self.assertEqual(response.status_code,200,response.text);self.assertEqual(response.json()['data']['invoices'],[])
  direct=self.unwrap(self.erp.get(integration.bridge.BASE+'balance-prueba/',params={'provider_id':self.provider,'fecha_corte':self.day}).json());self.assertEqual(direct['total_debit'],'15.00');self.assertEqual(direct['total_credit'],'15.00')
 def test_unavailable_account_cannot_enter_shared_posting_contract(self):
  body=self.prepare_recognition();body['account_mapping']['receivable']=str(uuid.uuid4());self.assertIn(self.direct('revisar-reconocimiento-reserva',body).status_code,[400,409,422]);self.assertIn(self.command('review_recognition',body).status_code,[400,409,422])
 def test_valid_native_post_is_exact_and_both_reports_agree(self):
  fact,capture=self.capture();body={'invoice_id':capture['invoice_id'],'selection':fact['items'],'settlement_account_id':fact['settlement_account_id'],'economic_fact':'GOODS_OR_SERVICES_RECEIVED','evidence_digest':'c'*64,'expected_revision':0,'confirmed':True};review=self.command('review_native_purchase',body);self.assertEqual(review.status_code,200,review.text)
  posted=self.command('post_native_purchase',{'invoice_id':capture['invoice_id'],'review_id':review.json()['data']['review_id'],'confirmed':True});self.assertEqual(posted.status_code,200,posted.text)
  direct=self.unwrap(self.erp.get(integration.bridge.BASE+'balance-prueba/',params={'provider_id':self.provider,'fecha_corte':self.day}).json());corporate=self.client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':self.day});self.assertEqual(corporate.status_code,200,corporate.text);self.assertEqual(corporate.json()['data'],direct);self.assertEqual(direct['total_debit'],'134.00');self.assertEqual(direct['total_credit'],'134.00')
if __name__=='__main__':unittest.main()
