"""Native purchase responses cannot invent financial success or unsafe identities."""
import copy,unittest,uuid
from app.services.native_purchase_contract import validate
class NativePurchaseContractChecks(unittest.TestCase):
 def setUp(self):
  self.context={'tenant_id':str(uuid.uuid4()),'provider_id':str(uuid.uuid4())};self.invoice=7
  self.page={'company_id':self.context['tenant_id'],'provider_id':self.context['provider_id'],'read_only':True,'ledger_written':False,'documents_returned':False,'invoices':[{'invoice_id':7,'supplier_id':5,'number':'SYNTHETIC-1','issue_date':'2026-11-09','subtotal':'100.00','tax':'19.00','gross':'119.00','state':'POR_PAGAR'}],'next_after_id':None}
 def test_valid_page_has_exact_decimal_strings(self):
  self.assertIsNone(validate('native_purchase_sources',self.page,{'after_id':None},self.context))
 def test_foreign_company_cannot_supply_native_result(self):
  self.page['company_id']=str(uuid.uuid4())
  with self.assertRaises(ValueError):validate('native_purchase_sources',self.page,{'after_id':None},self.context)
 def test_unsafe_or_ambiguous_numeric_identifiers_refused(self):
  for value in [True,1.0,'7',0,9007199254740992]:
   data={'company_id':self.context['tenant_id'],'supplier_id':value,'ledger_written':False,'identity_verified':False,'replayed':False}
   with self.assertRaises(ValueError):validate('record_native_supplier',data,{},self.context)
 def test_money_floats_and_private_source_fields_refused(self):
  for change in [{'gross':119.0},{'medical_document':'SYNTHETIC PRIVATE'}]:
   data=copy.deepcopy(self.page);data['invoices'][0].update(change)
   with self.assertRaises(ValueError):validate('native_purchase_sources',data,{},self.context)
 def test_recovery_cannot_restore_approval(self):
  data={'company_id':self.context['tenant_id'],'invoice_id':7,'document_id':str(uuid.uuid4()),'read_only':True,'confirmations_restored':True,'native_source_verified':True,'source_matches_review':True,'posted':None}
  with self.assertRaises(ValueError):validate('native_purchase_state',data,{'invoice_id':7},self.context)
 def test_posting_cannot_claim_payment_or_other_invoice(self):
  base={'company_id':self.context['tenant_id'],'invoice_id':7,'document_id':str(uuid.uuid4()),'journal_id':str(uuid.uuid4()),'ledger_written':True,'native_source_verified':True,'regulatory_verified':False,'money_transferred':False,'fiscal_document_created':False,'replayed':False}
  validate('post_native_purchase',base,{'invoice_id':7},self.context)
  for change in [{'invoice_id':8},{'ledger_written':False},{'money_transferred':True},{'regulatory_verified':True}]:
   with self.assertRaises(ValueError):validate('post_native_purchase',{**base,**change},{'invoice_id':7},self.context)
if __name__=='__main__':unittest.main()
