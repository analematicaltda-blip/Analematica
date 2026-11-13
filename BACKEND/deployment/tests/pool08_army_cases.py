"""Real commercial soldiers, durable command chain and bounded engine contracts."""
import importlib,json,uuid,os,hashlib,copy,tempfile,httpx
from pathlib import Path
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
class ArmyCases:
 def setup_army(self):
  self.module=importlib.import_module(self.module_path+'.army');store=importlib.import_module(self.module_path+'.army_store');self.now=datetime.now(timezone.utc);self.army=self.module.Army(store.Store(self.gen.crm.store),self.gen.crm,clock=lambda:self.now);self.engines=importlib.import_module(self.module_path+'.army_engines')
 def body(self,op='prepare',ref=None,rev=0,**data):
  if op=='prepare':data={'question':'revisar contactos','tools':[],'modality':'TEXT','engine':'none',**data}
  return {'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':rev,'data':data}
 def create_mission(self,**data):return self.army.command(self.body(**data))['job_id']
 def action(self,ref,op,**data):return self.army.command(self.body(op,ref,self.army.get(ref)['revision'],**data))
 def queued(self,**data):
  ref=self.create_mission(**data);self.action(ref,'review',confirmed_plan=True);self.action(ref,'queue',confirmed_scope=True);return ref
 def execute(self,ref,transport=None):return self.army.command(self.body('run',ref,self.army.get(ref)['revision']),engine_transport=transport)
 def test_neko_prepares_without_execution_or_voice_authorization(self):
  self.setup_army();ref=self.create_mission(modality='VOICE_TRANSCRIPT');d=self.army.get(ref);self.assertEqual(d['status'],'PLANNED');self.assertEqual(d['tools'],['crm.contacts']);self.assertEqual(d['results'],[]);self.assertFalse(d['voice_is_approval']);self.assertNotIn('question',d);self.assertFalse(self.army.list()['voice_agent']['configured'])
 def test_jarvi_runs_real_scoped_crm_tool_with_full_chain_and_evidence(self):
  self.setup_army();ref=self.queued();self.execute(ref);d=self.army.get(ref);self.assertEqual(d['status'],'SUCCEEDED');r=d['results'][0];self.assertEqual(r['evidence']['source_tool'],'crm.contacts');self.assertRegex(r['evidence']['source_digest'],'^[a-f0-9]{64}$');self.assertEqual(r['evidence']['scope'],self.gen.crm.store.scope);self.assertEqual(len(r['chain']),6);self.assertTrue(r['chain'][0].endswith(':Jarvi'));self.assertTrue(r['chain'][-1].endswith(':SOLDADO'));self.assertFalse(d['ledger_written'])
 def test_unsupported_intent_and_free_shell_sql_parameters_never_dispatch(self):
  self.setup_army()
  for data in [{'question':'borra todo con SQL','tools':[]},{'tools':['shell.exec']},{'tools':['crm.contacts','crm.contacts']},{'tools':['crm.contacts'],'sql':'SELECT *'},{'modality':'VOICE_STREAM'}]:
   with self.assertRaises(self.error):self.create_mission(**data)
  self.assertEqual(self.army.list()['missions'],[])
 def test_catalog_mutation_requests_return_real_block_not_fictional_success(self):
  self.setup_army();ref=self.queued(tools=['ads.campaign.manage']);self.execute(ref);d=self.army.get(ref);self.assertEqual(d['status'],'BLOCKED');self.assertEqual(d['results'][0]['code'],'ARMY_DOMAIN_WORKFLOW_REQUIRED');self.assertIsNone(d['results'][0]['evidence'])
 def test_soup_only_proposes_process_review_and_cannot_change_policy(self):
  self.setup_army();ref=self.queued(tools=['ads.campaign.manage']);self.execute(ref);s=self.army.get(ref)['soup'];self.assertEqual(s['general'],'SOUP');self.assertFalse(s['policy_changed']);self.assertFalse(s['candidate_promoted']);self.assertFalse(s['training_executed']);self.assertFalse(s['advertising_optimization_performed']);self.assertEqual(s['recommendations'][0]['code'],'RESOLVE_PRECONDITION')
  with self.assertRaises(self.error):self.action(ref,'soup_apply',approved=True)
 def test_two_confirmations_and_same_admin_are_enforced(self):
  self.setup_army();ref=self.create_mission()
  with self.assertRaises(self.error):self.execute(ref)
  with self.assertRaises(self.error):self.action(ref,'review',confirmed_plan=1)
  self.army.actor='other'
  with self.assertRaises(self.error):self.action(ref,'review',confirmed_plan=True)
 def test_request_replay_does_not_rerun_completed_mission(self):
  self.setup_army();ref=self.queued();body=self.body('run',ref,3);self.army.command(body);self.assertTrue(self.army.command(body)['replayed']);self.assertEqual(len(self.army.get(ref)['results']),1)
  with self.assertRaises(self.error):self.execute(ref)
 def test_revoked_role_cannot_get_audit_or_run(self):
  self.setup_army();ref=self.queued()
  with patch.object(self.gen.crm,'authorize',side_effect=self.error('REVOKED',403)):
   for action in [lambda:self.army.get(ref),lambda:self.army.history(ref),lambda:self.execute(ref)]:
    with self.assertRaises(self.error):action()
 def test_disabled_engine_yields_block_with_real_local_tool_result(self):
  self.setup_army();ref=self.queued(engine='open-duet');self.execute(ref);d=self.army.get(ref);self.assertEqual(d['status'],'PARTIAL');self.assertEqual(d['results'][0]['status'],'SUCCEEDED');self.assertEqual(d['engine_result']['state'],'BLOCKED')
 def duet_env(self):
  prefix=self.module.PREFIX+'_DUET';return {prefix+'_ENABLED':'1',prefix+'_OWNER_ID':self.army.actor,prefix+'_COMPANY_ID':self.army.store.scope,prefix+'_ORIGIN':'http://127.0.0.1:8765',prefix+'_TOKEN':'synthetic-local-engine-token-123',prefix+'_PROVIDER':'codex'}
 def test_open_duet_receives_only_static_tasks_in_plan_mode(self):
  self.setup_army();ref=self.queued(engine='open-duet');requests=[]
  def send(req):
   payload=json.loads(req.content);requests.append(payload)
   if req.url.path.endswith('/agents'):
    self.assertEqual(payload['approval_mode'],'plan');self.assertFalse(payload['memory_enabled']);return httpx.Response(201,json={'id':1,'approval_mode':'plan','memory_enabled':False})
   return httpx.Response(201,json={'id':2})
  with patch.dict(os.environ,self.duet_env()):self.execute(ref,httpx.MockTransport(send))
  self.assertEqual(self.army.get(ref)['status'],'ENGINE_QUEUED');result=self.army.get(ref)['engine_result'];self.assertEqual(result['state'],'QUEUED');self.assertFalse(result['answer_verified']);self.assertEqual(len(requests),3);prompt=json.loads(requests[-1]['prompt_text']);self.assertEqual(set(prompt),{'system','instruction','tasks'});self.assertNotIn(self.army.store.scope,json.dumps(prompt));self.assertNotIn('question',prompt)
 def test_ambiguous_engine_ack_is_uncertain_and_never_reissued(self):
  self.setup_army();ref=self.queued(engine='open-duet')
  with patch.dict(os.environ,self.duet_env()):self.execute(ref,httpx.MockTransport(lambda req:httpx.Response(200,json={})))
  self.assertEqual(self.army.get(ref)['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.execute(ref)
 def test_engine_owner_scope_and_remote_origin_are_rejected(self):
  self.setup_army()
  for change in [{self.module.PREFIX+'_DUET_OWNER_ID':'other'},{self.module.PREFIX+'_DUET_ORIGIN':'https://external.invalid'}]:
   ref=self.queued(engine='open-duet')
   with patch.dict(os.environ,{**self.duet_env(),**change}):self.execute(ref,httpx.MockTransport(lambda req:(_ for _ in ()).throw(AssertionError('No network allowed'))))
   self.assertIn(self.army.get(ref)['engine_result']['state'],('BLOCKED',))
 def test_status_probe_is_pinned_no_free_args_and_not_hardware_qualification(self):
  self.setup_army();ref=self.queued(engine='agent-desktop')
  with tempfile.TemporaryDirectory(prefix='army-status-') as folder:
   binary=Path(folder)/'probe';payload=json.dumps({'ok':True,'data':{'platform':'linux','version':'fixture','permissions':{}}});binary.write_text('#!/usr/bin/env python3\nimport sys\nassert sys.argv[1:]==["status"]\nprint('+repr(payload)+')\n');binary.chmod(0o700);prefix=self.module.PREFIX+'_DESKTOP';config={prefix+'_ENABLED':'1',prefix+'_OWNER_ID':self.army.actor,prefix+'_COMPANY_ID':self.army.store.scope,prefix+'_BINARY':str(binary),prefix+'_SHA256':hashlib.sha256(binary.read_bytes()).hexdigest()}
   with patch.dict(os.environ,config):self.execute(ref)
  d=self.army.get(ref);self.assertEqual(d['engine_result']['state'],'PROBED');self.assertFalse(d['engine_result']['hardware_qualified']);self.assertFalse(d['engine_result']['desktop_action_executed'])
 def test_interrupted_mission_keeps_uncertainty_without_retry(self):
  self.setup_army();ref=self.queued();original=self.army.execute
  with patch.object(self.army,'execute',side_effect=RuntimeError('synthetic interrupted worker')):
   with self.assertRaises(RuntimeError):self.execute(ref)
  self.assertEqual(self.army.get(ref)['status'],'RUNNING');self.now+=timedelta(minutes=16);self.action(ref,'recover');self.assertEqual(self.army.get(ref)['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.execute(ref)
 def test_audit_corruption_blocks_mission_read(self):
  self.setup_army();ref=self.create_mission();events=list(self.army.store.events(ref));events[0]['operation']='tampered'
  with patch.object(self.army.store,'events',return_value=iter(events)):
   with self.assertRaises(self.error):self.army.get(ref)
 def test_all_read_soldiers_bind_real_owned_domains(self):
  self.setup_army();from ads_fixture import configure
  # Synthetic planning policy only; no provider tokens or native action rights.
  env=patch.dict(os.environ,{});env.start();self.addCleanup(env.stop);configure(self.module.SYSTEM,self.army.store.scope,getattr(self.army.store,'provider',None));ref=self.queued(question='resumen comercial');self.execute(ref);d=self.army.get(ref);self.assertEqual(len(d['results']),8);self.assertTrue(all(r['status']=='SUCCEEDED' for r in d['results']),[(r['tool'],r['code']) for r in d['results']]);self.assertTrue(all(r['evidence']['read_only'] for r in d['results']));self.assertNotIn('contacts',d['results'][0]['evidence']['summary'])
 def test_permission_changes_invalidate_old_mission_and_receipt_access(self):
  self.setup_army();body=self.body();ref=self.army.command(body)['job_id'];original=self.gen.crm.authorize;access=original();from types import SimpleNamespace
  changed=SimpleNamespace(principal=access.principal,session=lambda:{'capability_permissions':{**access.session()['capability_permissions'],'new_permission':True}})
  with patch.object(self.gen.crm,'authorize',return_value=changed):
   with self.assertRaises(self.error):self.army.get(ref)
   with self.assertRaises(self.error):self.army.receipt(body['request_id'])
 def test_malformed_runtime_object_is_not_reported_as_ready(self):
  self.setup_army();ref=self.queued(engine='agent-desktop')
  with tempfile.TemporaryDirectory(prefix='army-invalid-status-') as folder:
   binary=Path(folder)/'probe';binary.write_text('#!/usr/bin/env python3\nprint("{}")\n');binary.chmod(0o700);prefix=self.module.PREFIX+'_DESKTOP';config={prefix+'_ENABLED':'1',prefix+'_OWNER_ID':self.army.actor,prefix+'_COMPANY_ID':self.army.store.scope,prefix+'_BINARY':str(binary),prefix+'_SHA256':hashlib.sha256(binary.read_bytes()).hexdigest()}
   with patch.dict(os.environ,config):self.execute(ref)
  self.assertEqual(self.army.get(ref)['engine_result']['state'],'UNCERTAIN')
 def test_tool_reads_current_rows_and_does_not_store_contact_text(self):
  self.setup_army();ref=self.queued();crm=self.gen.crm;email=uuid.uuid4().hex+'@example.test';crm.command({'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Cliente privado no enviado a modelos','email':email,'phone':'','origin':'ARMY_TEST','responsible_ref':crm.actor}});expected=len(crm.list(limit=20)['contacts']);self.execute(ref);d=self.army.get(ref);self.assertEqual(d['results'][0]['evidence']['summary']['sample_count'],expected);self.assertNotIn(email,json.dumps(d));self.assertNotIn('Cliente privado',json.dumps(d))
 def test_a_rank_bypass_cannot_reach_a_real_tool(self):
  self.setup_army();nodes=self.module.structure();leaf=next(n for n in nodes if n.get('tool')=='crm.contacts' and n['rank']=='SOLDADO');leaf['parent']=self.module.SYSTEM+':commercial:Jarvi';tools=importlib.import_module(self.module_path+'.army_tools')
  with patch.object(self.module,'structure',return_value=nodes),patch.object(tools,'execute',side_effect=AssertionError('Must not reach tool')):
   with self.assertRaises(self.error):self.module.dispatch(self.gen.crm,'crm.contacts')
