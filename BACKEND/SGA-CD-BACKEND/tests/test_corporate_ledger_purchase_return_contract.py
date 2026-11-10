import copy,unittest,uuid
from app.services.purchase_return_contract import validate
class ReturnContractChecks(unittest.TestCase):
 def setUp(self):
  self.ctx={'tenant_id':str(uuid.uuid4()),'provider_id':str(uuid.uuid4())};self.payload={'invoice_id':7};self.zero={k:'0.00' for k in ['net','tax','withholding','gross','settlement']};self.data={'schema':'sgacd-native-purchase-return-v1','native_source_verified':True,'company_id':self.ctx['tenant_id'],'invoice_id':7,'document_id':str(uuid.uuid4()),'returns':[],'revision':0,'history_digest':'a'*64,'returned':self.zero.copy(),'remaining':{'net':'100.00','tax':'19.00','withholding':'2.50','gross':'119.00','settlement':'116.50'},'currency':'COP','money_transferred':False,'fiscal_document_created':False,'regulatory_verified':False,'confirmations_restored':False,'read_only':True,'original_reversed':False,'ledger_written':False}
 def check(self):return validate('purchase_return_state',self.data,self.payload,self.ctx)
 def test_valid_read_only_capacity(self):self.check()
 def test_wrong_company_invoice_and_restored_approval_rejected(self):
  for change in [{'company_id':str(uuid.uuid4())},{'invoice_id':8},{'confirmations_restored':True}]:
   data=copy.deepcopy(self.data);data.update(change)
   with self.assertRaises(ValueError):validate('purchase_return_state',data,self.payload,self.ctx)
 def test_fake_cash_fiscal_success_and_read_writes_rejected(self):
  for key in ['money_transferred','fiscal_document_created','regulatory_verified','ledger_written']:
   self.data[key]=True
   with self.assertRaises(ValueError):self.check()
   self.data[key]=False
 def test_exact_amounts_and_component_sums_required(self):
  for change in [{'tax':19.0},{'net':'-1.00'},{'settlement':'119.00'}]:
   saved=copy.deepcopy(self.data);self.data['remaining'].update(change)
   with self.assertRaises(ValueError):self.check()
   self.data=saved
 def test_returned_amount_must_be_supported_by_history(self):
  self.data['returned']={'net':'25.00','tax':'4.75','withholding':'0.63','gross':'29.75','settlement':'29.12'}
  with self.assertRaises(ValueError):self.check()
 def test_post_cannot_invent_a_journal(self):
  self.data.update(ledger_written=True,journal_id=str(uuid.uuid4()),replayed=False)
  with self.assertRaises(ValueError):validate('post_purchase_return',self.data,self.payload,self.ctx)

class CorrectedReturnContractChecks(unittest.TestCase):
 def setUp(self):
  base=ReturnContractChecks();base.setUp();self.ctx=base.ctx;self.payload=base.payload;self.data=base.data;self.data['revision']=1;self.data['returns']=[{'return_id':str(uuid.uuid4()),'journal_id':str(uuid.uuid4()),'review_id':str(uuid.uuid4()),'revision':1,'totals':{'net':'25.00','tax':'4.75','withholding':'0.63','gross':'29.75','settlement':'29.12'},'proof_digest':'b'*64,'reversed':True,'reversal_journal_id':str(uuid.uuid4()),'reversal_digest':'c'*64}]
 def check(self):return validate('purchase_return_state',self.data,self.payload,self.ctx)
 def test_corrected_history_restores_only_active_amounts(self):self.check()
 def test_unproven_correction_cannot_free_capacity(self):
  self.data['returns'][0]['reversed']=False
  with self.assertRaises(ValueError):self.check()
 def test_counter_journal_cannot_replace_the_original(self):
  self.data['returns'][0]['reversal_journal_id']=self.data['returns'][0]['journal_id']
  with self.assertRaises(ValueError):self.check()

class ReversedOriginalContractChecks(unittest.TestCase):
 def test_full_reversal_requires_zero_remaining_capacity(self):
  base=ReturnContractChecks();base.setUp();base.data['original_reversed']=True
  with self.assertRaises(ValueError):base.check()
  base.data['remaining']=base.zero.copy();base.check();base.data['original_reversed']='true'
  with self.assertRaises(ValueError):base.check()
 def test_full_reversal_cannot_hide_an_active_return(self):
  base=CorrectedReturnContractChecks();base.setUp();base.data['original_reversed']=True;base.data['remaining']=base.zero.copy() if hasattr(base,'zero') else {k:'0.00' for k in base.data['remaining']}
  validate('purchase_return_state',base.data,base.payload,base.ctx)
  row=base.data['returns'][0]
  for key in ['reversed','reversal_journal_id','reversal_digest']:del row[key]
  base.data['returned']=row['totals'].copy()
  with self.assertRaises(ValueError):validate('purchase_return_state',base.data,base.payload,base.ctx)
