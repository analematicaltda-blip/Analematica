"""Cross-backend POOL-08 contract conformance, without providers or databases."""
import copy
import importlib.util
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import unittest
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[3]
PATHS = {
 'sga-cd': 'BACKEND/SGA-CD-BACKEND/app/commercial/pool08',
 'erp-tur': 'BACKEND/SGA-ERP-TUR-BAKEND/gestion_comercial/pool08',
 'analematica': 'BACKEND/ANALEMATICA-BACKEND/gestion_comercial/pool08',
}
def load(system):
 spec=importlib.util.spec_from_file_location('pool08_'+system, ROOT/PATHS[system]/'contract.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
MODULES={key:load(key) for key in PATHS}
NOW=datetime(2026,11,11,12,tzinfo=timezone.utc)
def sample(system,tenant='tenant:1',actor='1',version='1.0',kind='SALE_PREPARATION'):
 body = {'schema_version':'1.0','system':system,'orchestration_id':str(uuid4()),'idempotency_key':str(uuid4()),'tenant_ref':tenant,'actor_ref':actor,'expires_at':(NOW+timedelta(minutes=5)).isoformat(),
 'lead_profile':{'customer_ref':'customer:1','consent_ref':'consent:1','origin_channel':'GMAIL'},
 'agent_chain_attribution':{'orchestrator':'JARVI','conversation':'NEKO','optimizer':'SOUP','creative_role':'CREATIVE_DIVISION'},
 'transaction_payload':{'offering_ref':'product:1','offering_kind':'PLATFORM_SERVICE','gross_fiat_amount':'50000.00','currency':'COP'},
 'sovereign_storage_dispatch':{'target_storage':'GOOGLE_DRIVE','encryption_algorithm':'AES-256-GCM','client_kms_key_reference':'client-kms-key-v1'},
 'task_graph':[{'id':str(uuid4()),'capability':'quote.prepare','depends_on':[]}]}
 if version == '1.1':
  body.update(schema_version=version,intent_kind=kind)
  if kind == 'CAPABILITY_PLAN':
   for key in ('lead_profile','transaction_payload','sovereign_storage_dispatch'):body.pop(key)
 return body

class ContractChecks(unittest.TestCase):
 def validate(self,module,body):return module.validate_intent(body,tenant_ref='tenant:1',actor_ref='1',now=NOW)
 def reject(self,change):
  for system,module in MODULES.items():
   body=sample(system);change(body)
   with self.subTest(system=system),self.assertRaises(module.ContractRejected):self.validate(module,body)
 def test_three_schemas_are_identical_valid_and_in_own_backends(self):
  schemas=[(ROOT/path/'commercial-intent.schema.json').read_bytes() for path in PATHS.values()]
  self.assertEqual(len(set(schemas)),1)
 def test_valid_draft_never_grants_execution_or_provider_certification(self):
  for system,module in MODULES.items():
   body=sample(system);before=copy.deepcopy(body);result=self.validate(module,body)
   self.assertEqual(result['state'],'VALIDATED_DRAFT');self.assertEqual(result['system'],system)
   for key in ('execution_authorized','payment_verified','fiscal_accepted','inventory_locked','storage_written','network_called'):self.assertIs(result[key],False)
   self.assertEqual(body,before)
 def test_all_capability_sets_match_without_claiming_execution(self):
  sets=[]
  for module in MODULES.values():
   catalog=module.capabilities();sets.append({row['id'] for row in catalog['capabilities']});self.assertFalse(catalog['execution_enabled'])
   self.assertTrue(all(row['pool08_execution_enabled'] is False for row in catalog['capabilities']))
  self.assertEqual(sets[0],sets[1]);self.assertEqual(sets[0],sets[2]);self.assertEqual(len(sets[0]),20)
 def test_soup_keeps_agent_optimization_and_not_creative_production(self):
  for module in MODULES.values():
   self.assertEqual(module.capabilities()['general_roles']['SOUP'],'AGENT_PROCESS_OPTIMIZATION')
   self.assertEqual(module.capabilities()['creative_role'],'CREATIVE_DIVISION_UNDER_JARVI')
 def test_reassigning_soup_is_not_silently_accepted(self):self.reject(lambda b:b['agent_chain_attribution'].update(creative_role='SOUP'))
 def test_unknown_roles_and_success_flags_rejected(self):self.reject(lambda b:b.update(execution_authorized=True))
 def test_foreign_company_actor_or_system_rejected(self):
  for key,value in [('tenant_ref','tenant:2'),('actor_ref','2'),('system','foreign')]:self.reject(lambda b:b.update({key:value}))
 def test_decimal_amount_cannot_be_float_boolean_negative_zero_or_exponent(self):
  for value in (50000.0,True,'-1.00','0.00','1e4','1.001','NaN'):
   self.reject(lambda b:b['transaction_payload'].update(gross_fiat_amount=value))
 def test_currency_is_explicit_and_not_assumed_usd(self):self.reject(lambda b:b['transaction_payload'].pop('currency'))
 def test_expiry_past_or_excessive_rejected(self):
  for expiry in (NOW,NOW-timedelta(seconds=1),NOW+timedelta(minutes=16)):
   self.reject(lambda b:b.update(expires_at=expiry.isoformat()))
 def test_naive_expiry_rejected(self):self.reject(lambda b:b.update(expires_at='2026-11-11T12:05:00'))
 def test_no_auth_token_in_storage_event(self):self.reject(lambda b:b['sovereign_storage_dispatch'].update(auth_context_token='not-a-real-token'))
 def test_no_passport_or_names_in_event(self):self.reject(lambda b:b['transaction_payload'].update(pax_manifest=[{'name':'Synthetic','doc_id':'not-real'}]))
 def test_declared_hash_is_not_a_payment_verifier(self):self.reject(lambda b:b['transaction_payload'].update(payment_verification_hash='0'*64))
 def test_uuid_casing_cannot_create_aliases_for_idempotency(self):self.reject(lambda b:b.update(orchestration_id='AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA'))
 def test_unknown_tool_not_accepted(self):self.reject(lambda b:b['task_graph'][0].update(capability='shell.execute'))
 def test_duplicate_dag_nodes_rejected(self):self.reject(lambda b:b['task_graph'].append(copy.deepcopy(b['task_graph'][0])))
 def test_self_and_missing_dependency_rejected(self):
  self.reject(lambda b:b['task_graph'][0].update(depends_on=[b['task_graph'][0]['id']]))
  self.reject(lambda b:b['task_graph'][0].update(depends_on=[str(uuid4())]))
 def test_cycle_rejected(self):
  def cycle(b):
   first=b['task_graph'][0];second={'id':str(uuid4()),'capability':'media.reel.render','depends_on':[first['id']]};first['depends_on']=[second['id']];b['task_graph'].append(second)
  self.reject(cycle)
 def test_deterministic_topology_and_fingerprint(self):
  for system,module in MODULES.items():
   b=sample(system);first=b['task_graph'][0];second={'id':str(uuid4()),'capability':'channel.video.publish','depends_on':[first['id']]};b['task_graph']=[second,first]
   x=self.validate(module,b);y=self.validate(module,json.loads(json.dumps(b,sort_keys=True)))
   self.assertEqual(x['topological_order'],[first['id'],second['id']]);self.assertEqual(x['fingerprint'],y['fingerprint'])
 def test_duplicate_fields_nonfinite_and_invalid_utf8_rejected(self):
  for module in MODULES.values():
   for raw in (b'{"a":1,"a":2}',b'{"a":NaN}',b'\xff'):
    with self.assertRaises(module.ContractRejected):module.decode(raw)
 def test_body_and_nesting_limits(self):
  for module in MODULES.values():
   for raw in (b' '* (module.MAX_BYTES+1),b'['*50+b'0'+b']'*50):
    with self.assertRaises(module.ContractRejected):module.decode(raw)
 def test_catalog_cannot_be_mutated_by_callers(self):
  for module in MODULES.values():
   module.capabilities()['capabilities'].clear();self.assertEqual(len(module.capabilities()['capabilities']),20)


 def test_legacy_schema_and_catalog_remain_available(self):
  for module in MODULES.values():
   self.assertEqual(module.contract_document('1.0')['schema']['properties']['schema_version']['const'],'1.0')
   self.assertEqual(len(module.capabilities('1.0')['capabilities']),15)
   self.assertEqual(module.validate_intent(sample(module.SYSTEM),tenant_ref='tenant:1',actor_ref='1',now=NOW)['schema_version'],'1.0')
 def test_schema_hashes_and_semantics_match_in_three_systems(self):
  import hashlib
  for version in ('1.0','1.1'):
   documents=[module.contract_document(version) for module in MODULES.values()]
   self.assertEqual(len({row['schema_digest'] for row in documents}),1)
   for row in documents:
    self.assertEqual(hashlib.sha256(json.dumps(row['schema'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),row['schema_digest'])
 def test_protocol_documents_cannot_be_mutated_by_client(self):
  for module in MODULES.values():
   document=module.contract_document();document['schema'].clear();document['limits'].clear()
   self.assertIn('properties',module.contract_document()['schema'])
 def test_nonfinancial_landing_and_campaign_plans_need_no_fake_sale(self):
  expected={'landing.page.manage','landing.lead.capture','campaign.email.bulk.send','campaign.sms_mms.send','campaign.whatsapp.multimedia.send'}
  for system,module in MODULES.items():
   body=sample(system,version='1.1',kind='CAPABILITY_PLAN')
   body['task_graph']=[{'id':str(uuid4()),'capability':key,'depends_on':[]} for key in sorted(expected)]
   value=self.validate(module,body);self.assertEqual(value['intent_kind'],'CAPABILITY_PLAN');self.assertFalse(value['execution_authorized'])
   self.assertEqual({node['capability'] for node in value['planned_tasks']},expected)
   self.assertTrue(all(node['state']=='REQUIRES_DOMAIN_BINDING' for node in value['planned_tasks']))
 def test_all_twenty_capabilities_fit_bounded_latest_graph(self):
  for system,module in MODULES.items():
   body=sample(system,version='1.1',kind='CAPABILITY_PLAN')
   body['task_graph']=[{'id':str(uuid4()),'capability':row['id'],'depends_on':[]} for row in module.capabilities()['capabilities']]
   self.assertEqual(len(self.validate(module,body)['topological_order']),20)
 def test_latest_financial_contract_requires_business_payload(self):
  for system,module in MODULES.items():
   for key in ('lead_profile','transaction_payload','sovereign_storage_dispatch'):
    body=sample(system,version='1.1');body.pop(key)
    with self.assertRaises(module.ContractRejected):self.validate(module,body)
 def test_nonfinancial_plan_cannot_smuggle_financial_payload(self):
  for system,module in MODULES.items():
   body=sample(system,version='1.1',kind='CAPABILITY_PLAN');body['transaction_payload']=sample(system)['transaction_payload']
   with self.assertRaises(module.ContractRejected):self.validate(module,body)
 def test_latest_version_requires_explicit_intent_kind(self):
  for system,module in MODULES.items():
   body=sample(system,version='1.1');body.pop('intent_kind')
   with self.assertRaises(module.ContractRejected):self.validate(module,body)
 def test_unsupported_and_conflicting_versions_rejected(self):
  for system,module in MODULES.items():
   body=sample(system,version='1.1')
   with self.assertRaisesRegex(module.ContractRejected,'CONTRACT_VERSION_MISMATCH'):
    module.validate_intent(body,tenant_ref='tenant:1',actor_ref='1',now=NOW,requested_version='1.0')
   for version in ('2.0','',True):
    with self.assertRaisesRegex(module.ContractRejected,'UNSUPPORTED_VERSION'):module.contract_document(version)
 def test_new_capability_is_not_silently_added_to_legacy_version(self):
  self.reject(lambda b:b['task_graph'][0].update(capability='landing.page.manage'))
 def test_boundary_limits_dag_size_and_expiry_edge(self):
  for system,module in MODULES.items():
   b=sample(system,version='1.1',kind='CAPABILITY_PLAN');b['expires_at']=(NOW+timedelta(minutes=15)).isoformat()
   b['task_graph']=[{'id':str(uuid4()),'capability':'landing.page.manage','depends_on':[]} for _ in range(32)]
   self.assertEqual(len(self.validate(module,b)['topological_order']),32)
   b['task_graph'].append({'id':str(uuid4()),'capability':'landing.page.manage','depends_on':[]})
   with self.assertRaises(module.ContractRejected):self.validate(module,b)
 def test_safe_audit_records_no_body_customer_or_token(self):
  for system,module in MODULES.items():
   body=sample(system,version='1.1');body['lead_profile']['customer_ref']='private-customer-reference'
   with self.assertLogs('pool08.audit',level='INFO') as capture:self.validate(module,body)
   self.assertNotIn('private-customer-reference',''.join(capture.output));self.assertIn('VALIDATED_DRAFT',''.join(capture.output))
   body['sovereign_storage_dispatch']['auth_context_token']='private-token-do-not-log'
   with self.assertLogs('pool08.audit',level='INFO') as capture:
    with self.assertRaises(module.ContractRejected):self.validate(module,body)
   self.assertNotIn('private-token-do-not-log',''.join(capture.output));self.assertIn('SCHEMA_INVALID',''.join(capture.output))
 def test_retries_are_deterministic_without_issuing_execution_grants(self):
  for system,module in MODULES.items():
   body=sample(system,version='1.1');first=self.validate(module,body);second=self.validate(module,body)
   self.assertEqual(first,second);self.assertFalse(first['execution_authorized']);self.assertFalse(first['storage_written'])


 def test_latest_cycle_and_false_payment_or_token_claims_are_rejected(self):
  for system,module in MODULES.items():
   body=sample(system,version='1.1',kind='CAPABILITY_PLAN');first=body['task_graph'][0];second={'id':str(uuid4()),'capability':'landing.page.manage','depends_on':[first['id']]};first['depends_on']=[second['id']];body['task_graph'].append(second)
   with self.assertRaisesRegex(module.ContractRejected,'DAG_CYCLE'):self.validate(module,body)
   for field,value in [('payment_verification_hash','0'*64),('pax_manifest',[{'doc_id':'private-document'}])]:
    sale=sample(system,version='1.1');sale['transaction_payload'][field]=value
    with self.assertRaises(module.ContractRejected):self.validate(module,sale)

if __name__=='__main__':unittest.main(verbosity=2)
