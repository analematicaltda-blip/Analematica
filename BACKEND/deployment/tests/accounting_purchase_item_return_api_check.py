"""Real private API and corporate conservation of concept-return capacity."""
import copy,runpy,unittest,sys,uuid
from pathlib import Path
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_purchase_item_returns_check.py')),run_name='item_return_api_fixture')
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'SGA-CD-BACKEND'))
from app.services.purchase_item_return_contract import validate
class ItemReturnApiChecks(unittest.TestCase):
 def setUp(self):
  self.base=fixture['ItemReturnChecks']();self.base.setUp();self.native=self.base.base;self.context={'tenant_id':str(self.native.company.pk),'provider_id':str(self.native.provider.pk),'ledger_actor_id':str(self.native.actor.pk)}
  self.payload={'invoice_id':self.base.capture['invoice_id'],'return_id':str(uuid.uuid4()),'selection':[{'item_id':self.base.ids[0],'net':'30.00'}],'entry_date':self.base.day,'document_digest':uuid.uuid4().hex*2,'evidence_digest':'c'*64,'expected_revision':0,'confirmed':True}
 def call(self,action,payload):return self.native.call(action,payload)
 def test_actual_api_review_post_capacity_recovery_and_contract(self):
  r=self.call('review_purchase_item_return',self.payload);self.assertEqual(r.status_code,200,r.data);validate('review_purchase_item_return',r.data,self.payload,self.context)
  payload={'invoice_id':self.payload['invoice_id'],'review_id':r.data['review_id'],'confirmed':True};a=self.call('post_purchase_item_return',payload);self.assertEqual(a.status_code,200,a.data);validate('post_purchase_item_return',a.data,payload,self.context)
  args={'invoice_id':self.payload['invoice_id']};s=self.call('purchase_item_return_state',args);self.assertEqual(s.status_code,200,s.data);validate('purchase_item_return_state',s.data,args,self.context);self.assertFalse(s.data['confirmations_restored']);self.assertTrue(self.call('post_purchase_item_return',payload).data['replayed'])
 def test_actual_correction_preserves_contract_and_releases_only_selected_net(self):
  r=self.call('review_purchase_item_return',self.payload);self.call('post_purchase_item_return',{'invoice_id':self.payload['invoice_id'],'review_id':r.data['review_id'],'confirmed':True})
  p={'invoice_id':self.payload['invoice_id'],'return_id':self.payload['return_id'],'request_id':str(uuid.uuid4()),'entry_date':self.base.day,'reason_code':'DATA_ENTRY_ERROR','evidence_digest':'d'*64,'expected_revision':1,'confirmed':True};v=self.call('review_purchase_item_return_void',p);self.assertEqual(v.status_code,200,v.data);validate('review_purchase_item_return_void',v.data,p,self.context)
  p={'invoice_id':self.payload['invoice_id'],'review_id':v.data['review_id'],'confirmed':True};a=self.call('void_purchase_item_return',p);self.assertEqual(a.status_code,200,a.data);validate('void_purchase_item_return',a.data,p,self.context);self.assertTrue(all(i['returned']['net']=='0.00' for i in a.data['items']))
 def test_tampered_allocation_or_capacity_is_rejected_at_corporate_boundary(self):
  r=self.call('review_purchase_item_return',self.payload).data
  for mutate in [lambda x:x['preview']['allocations'][0].update(new_net='99.00'),lambda x:x['preview']['allocations'][0]['components'][0].update(delta_amount='99.00'),lambda x:x.update(money_transferred=True),lambda x:x['preview']['lines'][0].update(credit='99.00')]:
   bad=copy.deepcopy(r);mutate(bad)
   with self.assertRaises(ValueError):validate('review_purchase_item_return',bad,self.payload,self.context)
  a=self.base.post(self.base.review());bad=copy.deepcopy(a);bad['items'][0]['available_net']='999.00'
  with self.assertRaises(ValueError):validate('post_purchase_item_return',bad,{'invoice_id':self.payload['invoice_id']},self.context)
 def test_private_api_rejects_spoofed_context_and_missing_confirmations(self):
  self.assertEqual(self.call('review_purchase_item_return',{**self.payload,'company_id':str(uuid.uuid4())}).status_code,400)
  self.assertEqual(self.call('review_purchase_item_return',{**self.payload,'confirmed':False}).status_code,400)
  r=self.call('review_purchase_item_return',self.payload);self.assertEqual(self.call('post_purchase_item_return',{'invoice_id':self.payload['invoice_id'],'review_id':r.data['review_id'],'confirmed':False}).status_code,400)
if __name__=='__main__':unittest.main()
