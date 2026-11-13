"""Generation contract, actual stores, controlled local inference transport. Not AI quality qualification."""
import base64,copy,hashlib,io,json,uuid
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
import httpx
from PIL import Image

class GenerationCases:
 def body(self,op='create',ref=None,rev=0,**data):
  if op=='create':data={'title':'Borrador propio','kind':'COPY','prompt':'Describe un servicio sin inventar precios.','profile_id':'text','max_cost_units':100,'confirmed_input_rights':True,**data}
  return dict(request_id=str(uuid.uuid4()),operation=op,job_id=ref,expected_revision=rev,data=data)
 def create(self,**data):return self.gen.command(self.body(**data))['job_id']
 def provider(self,kind='text',bad=None):
  buffer=io.BytesIO();Image.new('RGB',(512,512),(20,70,100)).save(buffer,format='PNG');image=base64.b64encode(buffer.getvalue()).decode()
  self.calls=[]
  def handle(request):
   self.calls.append((request.method,str(request.url)))
   self.assertIn(request.url.host,['127.0.0.1']);self.assertIsNone(request.headers.get('authorization'))
   if bad=='timeout':raise httpx.ReadTimeout('SENSITIVE_PROVIDER_EXCEPTION',request=request)
   if request.url.path=='/api/tags':return httpx.Response(200,json={'models':[{'name':'copy:1','digest':('b' if bad=='digest' else 'a')*64}]})
   if request.url.path=='/api/generate':
    body=json.loads(request.content);self.assertFalse(body['stream']);self.assertEqual(body['options']['num_predict'],64)
    return httpx.Response(200,json={'done':True,'model':'copy:1','response':'' if bad=='empty' else 'Borrador de prueba, pendiente de revisión.','prompt_eval_count':40,'eval_count':10 if bad!='usage' else 1000})
   if request.url.path=='/sdapi/v1/sd-models':return httpx.Response(200,json=[{'model_name':'diffusion-one','sha256':'a'*64,'title':'diffusion-one [aaaaaaaaaa]'}])
   if request.url.path=='/sdapi/v1/txt2img':
    body=json.loads(request.content);self.assertEqual(body['batch_size'],1);self.assertFalse(body['save_images'])
    return httpx.Response(200,json={'images':[image],'info':json.dumps({'sd_model_hash':'a'*10})})
   raise AssertionError('Unexpected local endpoint')
  def factory(**kwargs):
   self.assertFalse(kwargs['follow_redirects']);self.assertFalse(kwargs['trust_env']);return httpx.Client(transport=httpx.MockTransport(handle),**kwargs)
  return factory
 def finish(self,ref,kind='text'):
  item,token=self.gen.claim(ref);result=self.providers.generate(item,client_factory=self.provider(kind));self.gen.finish(ref,token,result=result);return self.gen.get(ref)
 def test_create_and_replay_are_private_and_exactly_once(self):
  body=self.body();r=self.gen.command(body);self.assertEqual(self.gen.command(body)['job_id'],r['job_id']);self.assertTrue(self.gen.command(body)['replayed']);self.assertEqual(len(list(self.gen.store.all_jobs())),1);self.assertEqual(self.gen.view(r['job_id'])['status'],'QUEUED');self.assertNotIn('claim_token_hash',self.gen.view(r['job_id']));self.assertFalse(self.gen.view(r['job_id'])['published'])
  different=copy.deepcopy(body);different['data']['prompt']='Otro contenido'
  with self.assertRaises(self.error):self.gen.command(different)
 def test_text_worker_result_requires_separate_review(self):
  ref=self.create();job=self.finish(ref);raw,mime=self.gen.bytes(ref);self.assertEqual(mime,'text/plain');self.assertIn(b'Borrador',raw);self.assertEqual(job['trace']['model_digest'],'a'*64);self.assertFalse(job['rights_authenticity_verified']);self.assertIsNone(job['cost']['actual_money']);self.assertEqual(job['cost']['state'],'CONSUMED_ESTIMATE')
  with self.assertRaises(self.error):self.gen.command(self.body('review',ref,3,confirmed_content=True,confirmed_rights=False,note='Revisión'))
  self.gen.command(self.body('review',ref,3,confirmed_content=True,confirmed_rights=True,note='Revisión humana sintética'));self.assertEqual(self.gen.get(ref)['status'],'REVIEWED');self.assertFalse(self.gen.get(ref)['published'])
 def test_image_result_uses_validated_local_model_and_decoded_private_bytes(self):
  ref=self.create(kind='IMAGE',profile_id='image');job=self.finish(ref,'image');raw,mime=self.gen.bytes(ref);self.assertEqual(mime,'image/png');self.assertEqual(Image.open(io.BytesIO(raw)).size,(512,512));self.assertEqual(hashlib.sha256(raw).hexdigest(),job['result']['sha256']);self.assertFalse(job['rights_authenticity_verified'])
 def test_missing_model_configuration_has_explicit_error_without_fake_job(self):
  with patch.dict('os.environ',{'COMMERCIAL_GENERATION_PROFILES':'{}'}):
   with self.assertRaises(self.error) as e:self.create()
  self.assertEqual(e.exception.status,503);self.assertEqual(list(self.gen.store.all_jobs()),[])
 def test_configuration_cannot_add_url_and_prompt_cannot_supply_a_tool(self):
  bad=copy.deepcopy(self.config);bad[self.config_key]['text']['url']='https://example.test/secret'
  with patch.dict('os.environ',{'COMMERCIAL_GENERATION_PROFILES':json.dumps(bad)}):
   with self.assertRaises(self.error):self.create()
  body=self.body();body['data']['tool']='shell'
  with self.assertRaises(self.error):self.gen.command(body)
 def test_budget_and_input_authorization_are_required(self):
  for data in [dict(max_cost_units=99),dict(max_cost_units=True),dict(confirmed_input_rights=False),dict(prompt='x'*3001),dict(kind='IMAGE')]:
   with self.subTest(data=list(data)):
    with self.assertRaises(self.error):self.create(**data)
  self.assertEqual(list(self.gen.store.all_jobs()),[])
 def test_model_digest_timeout_empty_output_and_usage_errors_never_succeed(self):
  for bad in ['digest','timeout','empty','usage']:
   ref=self.create();item,token=self.gen.claim(ref)
   with self.assertRaises(self.error) as e:self.providers.generate(item,client_factory=self.provider(bad=bad))
   self.gen.finish(ref,token,error_code=str(e.exception));job=self.gen.get(ref);self.assertEqual(job['status'],'FAILED');self.assertEqual(job['cost']['state'],'UNKNOWN');self.assertIsNone(job['result']);self.assertNotIn('SENSITIVE',job['error_code'])
 def test_cancel_does_not_dispatch_or_leave_reserved_credit(self):
  ref=self.create();self.gen.command(self.body('cancel',ref,1));self.assertEqual(self.gen.get(ref)['cost']['state'],'RELEASED')
  with self.assertRaises(self.error):self.gen.claim(ref)
 def test_claim_is_once_and_company_serialized(self):
  first=self.create();second=self.create();self.gen.claim(first)
  with self.assertRaises(self.error):self.gen.claim(first)
  with self.assertRaises(self.error):self.gen.claim(second)
  self.assertEqual(self.gen.get(second)['status'],'QUEUED')
 def test_stale_worker_does_not_store_result_or_automatically_retry(self):
  ref=self.create();item,token=self.gen.claim(ref);result=self.providers.generate(item,client_factory=self.provider());now=datetime.now(timezone.utc)+timedelta(minutes=16);self.gen.clock=lambda:now;self.gen.command(self.body('recover',ref,2));self.assertEqual(self.gen.get(ref)['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.gen.finish(ref,token,result=result)
  self.assertIsNone(self.gen.store.result(ref))
  with self.assertRaises(self.error):self.gen.claim(ref)
 def test_changed_configuration_before_claim_does_not_dispatch(self):
  ref=self.create();bad=copy.deepcopy(self.config);bad[self.config_key]['text']['model_digest']='b'*64
  with patch.dict('os.environ',{'COMMERCIAL_GENERATION_PROFILES':json.dumps(bad)}):job,token=self.gen.claim(ref)
  self.assertIsNone(token);self.assertEqual(job['status'],'FAILED');self.assertEqual(self.gen.get(ref)['cost']['state'],'RELEASED')
 def test_result_corruption_and_event_index_corruption_are_blocked(self):
  ref=self.create();self.finish(ref);self.corrupt_result(ref)
  with self.assertRaises(self.error):self.gen.bytes(ref)
  self.corrupt_event(ref)
  with self.assertRaises(self.error):self.gen.get(ref)
 def test_worker_disabled_is_an_explicit_error(self):
  from importlib import import_module
  worker=import_module(self.module_path+'.generation_worker')
  with patch.dict('os.environ',{'COMMERCIAL_GENERATION_WORKER_ENABLED':'0'}):
   with self.assertRaises(self.error):worker.run_once()
 def test_existing_catalog_preserves_models_and_five_engines_without_enabling_them(self):
  value=self.gen.profiles();self.assertEqual(len(value['catalog']['engines']),5);self.assertIn('gemma3-4b-desktop',[x['id'] for x in value['catalog']['models']]);self.assertFalse(value['runtime_qualified']);self.assertFalse(value['catalog']['runtime_qualified_here'])
 def test_remote_profile_is_blocked_without_scoped_approval(self):
  cfg=copy.deepcopy(self.config);cfg[self.config_key]['text']['adapter']='node6-text'
  with patch.dict('os.environ',{'COMMERCIAL_GENERATION_PROFILES':json.dumps(cfg),'COMMERCIAL_GENERATION_REMOTE_APPROVALS':'{}'}):
   with self.assertRaises(self.error) as e:self.create()
  self.assertEqual(str(e.exception),'GENERATION_REMOTE_APPROVAL_REQUIRED');self.assertEqual(list(self.gen.store.all_jobs()),[])
 def test_endpoint_registry_cannot_send_prompts_or_keys_to_arbitrary_hosts(self):
  from importlib import import_module
  system=import_module(self.module_path+'.contract').SYSTEM
  for address in ['http://169.254.169.254:8080','https://example.test:8080','http://user:pass@localhost:8080','http://localhost:8080/a?token=x']:
   with patch.dict('os.environ',{'COMMERCIAL_GENERATION_ENDPOINTS':json.dumps({system:{'colibri':address}})}):
    with self.assertRaises(self.error):self.providers.endpoint('colibri')
 def test_colibri_uses_documented_openai_compatible_local_protocol(self):
  cfg=copy.deepcopy(self.config);cfg[self.config_key]['text']['adapter']='colibri';cfg[self.config_key]['text']['model']='colibri-test'
  with patch.dict('os.environ',{'COMMERCIAL_GENERATION_PROFILES':json.dumps(cfg)}):ref=self.create();item,token=self.gen.claim(ref)
  def handle(request):
   if request.url.path=='/v1/models':return httpx.Response(200,json={'data':[{'id':'colibri-test'}]})
   self.assertEqual(request.url.path,'/v1/chat/completions');self.assertEqual(json.loads(request.content)['model'],'colibri-test');return httpx.Response(200,json={'model':'colibri-test','choices':[{'message':{'content':'Texto de contrato local'}}],'usage':{'prompt_tokens':10,'completion_tokens':8}})
  def client(**kwargs):return httpx.Client(transport=httpx.MockTransport(handle),**kwargs)
  result=self.providers.generate(item,client_factory=client);self.gen.finish(ref,token,result=result);self.assertEqual(self.gen.get(ref)['trace']['adapter'],'colibri');self.assertEqual(self.gen.get(ref)['trace']['model_digest_verification'],'OPERATOR_DECLARATION')
 def test_node6_reuses_only_explicit_scoped_secret_and_remote_authorization(self):
  cfg=copy.deepcopy(self.config);cfg[self.config_key]['text']['adapter']='node6-text';cfg[self.config_key]['text']['model']='gemini-test'
  approval_key=self.config_key+':text';fingerprint=self.providers.digest(cfg[self.config_key]['text'])
  values={'COMMERCIAL_GENERATION_PROFILES':json.dumps(cfg),'COMMERCIAL_GENERATION_REMOTE_APPROVALS':json.dumps({approval_key:fingerprint}),'COMMERCIAL_GENERATION_SECRET_BINDINGS':json.dumps({approval_key:'COMMERCIAL_GENERATION_SECRET_TEST'}),'COMMERCIAL_GENERATION_SECRET_TEST':'synthetic-local-node-token'}
  def handle(request):
   self.assertEqual(request.headers['authorization'],'Bearer synthetic-local-node-token')
   if request.url.path=='/status':return httpx.Response(200,json={'text_model':'gemini-test'})
   self.assertEqual(request.url.path,'/studio/script');return httpx.Response(200,json={'model':'gemini-test','provider':'gemini','text':'Guion del transporte de prueba'})
  def client(**kwargs):return httpx.Client(transport=httpx.MockTransport(handle),**kwargs)
  with patch.dict('os.environ',values):
   ref=self.create();item,token=self.gen.claim(ref);result=self.providers.generate(item,client_factory=client);self.gen.finish(ref,token,result=result)
  self.assertEqual(self.gen.get(ref)['trace']['remote_provider'],'gemini');self.assertNotIn('synthetic-local-node-token',json.dumps(self.gen.view(ref)))
 def test_remote_authorization_revocation_blocks_queued_work(self):
  cfg=copy.deepcopy(self.config);cfg[self.config_key]['text']['adapter']='node6-text';key=self.config_key+':text';approved={key:self.providers.digest(cfg[self.config_key]['text'])}
  with patch.dict('os.environ',{'COMMERCIAL_GENERATION_PROFILES':json.dumps(cfg),'COMMERCIAL_GENERATION_REMOTE_APPROVALS':json.dumps(approved)}):ref=self.create()
  with patch.dict('os.environ',{'COMMERCIAL_GENERATION_PROFILES':json.dumps(cfg),'COMMERCIAL_GENERATION_REMOTE_APPROVALS':'{}'}):receipt,token=self.gen.claim(ref)
  self.assertIsNone(token);self.assertEqual(self.gen.get(ref)['status'],'FAILED');self.assertEqual(self.gen.get(ref)['cost']['state'],'RELEASED')
