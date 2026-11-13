"""Actual own store trace, permissions, unavailable sources and privacy boundaries."""
import importlib,uuid,copy
from unittest.mock import patch
class OperationsCases:
 def setup_ops(self):
  self.module=importlib.import_module(self.module_path+'.operations');self.ops=self.module.Operations(self.gen.crm);self.army=importlib.import_module(self.module_path+'.army_api').service(self.gen.crm)
 def mission(self):return self.army.command({'request_id':str(uuid.uuid4()),'operation':'prepare','job_id':None,'expected_revision':0,'data':{'question':'revisar contactos','tools':[],'modality':'TEXT','engine':'none'}})['job_id']
 def test_trace_verifies_real_owned_chain_without_contact_content(self):
  self.setup_ops();ref=self.mission();r=self.ops.trace('army',ref);self.assertTrue(r['chain_verified']);self.assertEqual(len(r['events']),1);self.assertNotIn('receipt',r['events'][0]);self.assertFalse(r['ledger_or_provider_action']);self.assertEqual(r['scope'],self.gen.crm.store.scope)
 def test_tampered_history_rejected(self):
  self.setup_ops();ref=self.mission();store=self.ops.store('army');events=list(store.events(ref));events[0]['operation']='tampered'
  with patch.object(self.ops,'store',return_value=store),patch.object(store,'events',return_value=iter(events)):
   with self.assertRaises(self.error):self.ops.trace('army',ref)
 def test_manager_role_is_rechecked_and_user_cannot_select_modules(self):
  self.setup_ops()
  with self.assertRaises(self.error):self.ops.trace('../crm',str(uuid.uuid4()))
  with patch.object(self.gen.crm,'authorize',side_effect=self.error('REVOKED',403)):
   with self.assertRaises(self.error):self.ops.health()
 def test_missing_schema_is_unavailable_not_zero_or_qualified(self):
  self.setup_ops()
  with patch.object(self.ops,'store',side_effect=self.error('SCHEMA_INSTALL_REQUIRED',503)):
   r=self.ops.health()
  self.assertEqual(r['state'],'PARTIAL');self.assertTrue(all(x['sample_count'] is None for x in r['sources']));self.assertFalse(r['hardware_or_production_qualified']);self.assertEqual(r['provider_calls'],0);self.assertEqual(r['ledger_writes'],0)

 def test_trace_respects_creator_private_scope(self):
  self.setup_ops();ref=self.mission();self.gen.crm.actor='other-actor'
  with self.assertRaises(self.error):self.ops.trace('army',ref)

 def test_payments_and_capture_are_not_omitted(self):
  self.setup_ops();self.assertEqual(self.module.DOMAINS['payments'],'payment_store');self.assertEqual(self.module.DOMAINS['capture'],'capture_store')
 def test_committed_revision_during_trace_is_retried_not_called_corruption(self):
  self.setup_ops();ref=self.mission();store=self.ops.store('army');original=store.events;calls=[]
  def racing_events(key):
   calls.append(key)
   if len(calls)==1:self.army.command({'request_id':str(uuid.uuid4()),'operation':'cancel','job_id':ref,'expected_revision':1,'data':{}})
   return original(key)
  with patch.object(self.ops,'store',return_value=store),patch.object(store,'events',side_effect=racing_events):r=self.ops.trace('army',ref)
  self.assertEqual(r['revision'],2);self.assertEqual(len(r['events']),2);self.assertEqual(len(calls),2)
 def test_continuously_changing_record_has_bounded_retry(self):
  self.setup_ops();ref=self.mission();store=self.ops.store('army');initial=copy.deepcopy(store.get(ref));calls=[]
  def changing(key):
   calls.append(key);return {**initial,'changed_during_probe':len(calls)}
  with patch.object(self.ops,'store',return_value=store),patch.object(store,'get',side_effect=changing):
   with self.assertRaisesRegex(self.error,'OPERATIONS_CHANGED_RETRY'):self.ops.trace('army',ref)
  self.assertEqual(len(calls),4)
 def test_health_uses_verified_revision_for_sample_counts(self):
  self.setup_ops();ref=self.mission();store=self.ops.store('army');initial=copy.deepcopy(store.get(ref));self.army.command({'request_id':str(uuid.uuid4()),'operation':'cancel','job_id':ref,'expected_revision':1,'data':{}})
  with patch.dict(self.module.DOMAINS,{'army':'army_store'},clear=True),patch.object(self.ops,'store',return_value=store),patch.object(store,'list',return_value=([initial],False)):r=self.ops.health()
  self.assertEqual(r['sources'][0]['counts_by_state'],{'CANCELLED':1})
