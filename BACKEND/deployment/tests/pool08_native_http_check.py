"""Native commercial boundaries: real WSGI/JWT, disposable data, no money or providers."""
import runpy,unittest,json,os,sys,subprocess,tempfile,queue,threading
import httpx
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
fixture=runpy.run_path(str(Path(__file__).with_name('accounting_army_http_check.py')),run_name='pool08_native_fixture')
contracts=runpy.run_path(str(Path(__file__).with_name('pool08_contract_check.py')),run_name='pool08_contract_fixture')
class NativeCommercialChecks(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  fixture['NativeArmiesHTTP'].setUpClass.__func__(cls)
  cls.extra={}
  for system in ('sga-cd','gateway'):
   private=tempfile.TemporaryDirectory(prefix='pool08-http-');cls.addClassCleanup(private.cleanup)
   log=tempfile.TemporaryFile();cls.addClassCleanup(log.close)
   command=[sys.executable,str(Path(__file__).with_name('pool08_http_fixture.py')),'--system',system,'--directory',private.name]
   if system=='gateway':
    native=cls.servers['analematica'][0].base_url
    command += ['--native-origin','http://localhost:'+str(native.port)]
   process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=log,text=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
   def stop(process=process):
    process.terminate()
    try:process.wait(timeout=8)
    except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
    process.stdout.close()
   cls.addClassCleanup(stop)
   ready=queue.Queue()
   def read(process=process,ready=ready):
    for line in process.stdout:
     if line.startswith('READY '):ready.put(int(line.split()[1]));return
   threading.Thread(target=read,daemon=True).start()
   try:port=ready.get(timeout=35)
   except queue.Empty:raise RuntimeError('POOL08 ASGI fixture startup failed; no provider was contacted') from None
   cred=json.loads((Path(private.name)/'sga.json').read_text()) if system=='sga-cd' else cls.servers['analematica'][1]
   client=httpx.Client(base_url='http://127.0.0.1:'+str(port),trust_env=False,timeout=20,headers={'Authorization':'Bearer '+cred['token'],'Host':'localhost'})
   cls.addClassCleanup(client.close);cls.extra[system]=(client,cred)

 tearDownClass=classmethod(fixture['NativeArmiesHTTP'].tearDownClass.__func__)
 def prefix(self,system):return '/api/v1/commercial-unified/' if system=='analematica' else '/api/v1/mi-negocio/comercial/unified/'
 def unwrap(self,response):
  self.assertEqual(response.status_code,200,response.text);value=response.json();return value['data'] if value.get('success') is True else value
 def draft(self,system):
  client,cred=self.servers[system];context=self.unwrap(client.get(self.prefix(system)+'capabilities/',params={'provider_id':cred['provider_id']}))['context']
  body=contracts['sample'](system,context['tenant_ref'],context['actor_ref']);body['expires_at']=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat();return body
 def test_native_catalog_and_validated_draft_keep_no_execution(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system];body=self.draft(system)
   result=client.post(self.prefix(system)+'intents/validate/',params={'provider_id':cred['provider_id']},json=body)
   data=self.unwrap(result);self.assertEqual(data['system'],system);self.assertFalse(data['execution_authorized']);self.assertFalse(data['network_called']);self.assertEqual(result.headers['cache-control'],'no-store')
 def test_other_user_and_anonymous_cannot_inspect_company_capabilities(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system];url=self.prefix(system)+'capabilities/';query={'provider_id':cred['provider_id']}
   self.assertEqual(client.get(url,params=query,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,403)
   self.assertEqual(client.get(url,params=query,headers={'Authorization':''}).status_code,401)
 def test_claimed_other_actor_or_company_cannot_validate(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system]
   for key,value in [('tenant_ref',str(uuid4())),('actor_ref','forged-actor')]:
    body=self.draft(system);body[key]=value
    response=client.post(self.prefix(system)+'intents/validate/',params={'provider_id':cred['provider_id']},json=body);self.assertEqual(response.status_code,403);self.assertEqual(response.headers['cache-control'],'no-store')
 def test_tokens_duplicate_fields_and_oversized_body_rejected(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system];url=self.prefix(system)+'intents/validate/';query={'provider_id':cred['provider_id']}
   for raw,status in [('{"a":1,"a":2}',400),(' '*17000,413)]:
    self.assertEqual(client.post(url,params=query,content=raw,headers={'content-type':'application/json'}).status_code,status)
   body=self.draft(system);body['sovereign_storage_dispatch']['auth_context_token']='fake-secret'
   self.assertEqual(client.post(url,params=query,json=body).status_code,422)
 def test_missing_or_repeated_company_selection_rejected(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system];url=self.prefix(system)+'capabilities/'
   self.assertEqual(client.get(url).status_code,400)
   self.assertEqual(client.get(url,params=[('provider_id',cred['provider_id']),('provider_id',cred['provider_id'])]).status_code,400)
 def test_tourism_is_not_a_commercial_erp(self):
  client,cred=self.servers['turismo']
  for prefix in ('/api/v1/commercial-unified/','/api/v1/mi-negocio/comercial/unified/'):
   self.assertEqual(client.get(prefix+'capabilities/',params={'provider_id':cred['provider_id']}).status_code,404)

 def targets(self):
  for system in ('erp-tur','analematica'):
   client,cred=self.servers[system]
   yield system,client,{'provider_id':cred['provider_id']},self.prefix(system)
  yield 'sga-cd',self.extra['sga-cd'][0],{},'/api/v1/commercial-unified/'
  cred=self.servers['analematica'][1]
  yield 'analematica',self.extra['gateway'][0],{'provider_id':cred['provider_id']},'/api/v1/commercial-unified/'
 def latest(self,system,client,query,prefix,kind='CAPABILITY_PLAN'):
  context=self.unwrap(client.get(prefix+'capabilities'+('' if system=='sga-cd' else '/'),params=query))['context']
  body=contracts['sample'](system,context['tenant_ref'],context['actor_ref'],version='1.1',kind=kind)
  body['expires_at']=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
  return body
 def test_all_backends_and_gateway_discover_equal_versioned_schemas(self):
  import hashlib
  for version,count in [('1.0',15),('1.1',20)]:
   hashes=[]
   for system,client,query,prefix in self.targets():
    headers={'X-POOL08-Contract-Version':version}
    response=client.get(prefix+'contract/',params=query,headers=headers) if system!='sga-cd' else client.get(prefix+'contract',params=query,headers=headers)
    document=self.unwrap(response);hashes.append(document['schema_digest'])
    self.assertEqual(document['schema_version'],version);self.assertEqual(response.headers['x-pool08-contract-version'],version)
    route=prefix+'capabilities'+('' if system=='sga-cd' else '/')
    self.assertEqual(len(self.unwrap(client.get(route,params=query,headers=headers))['capabilities']),count)
    self.assertEqual(response.headers['cache-control'],'no-store')
   self.assertEqual(len(set(hashes)),1)
 def test_all_systems_plan_twenty_capabilities_without_a_fake_financial_payload(self):
  for system,client,query,prefix in self.targets():
   route=prefix+'capabilities'+('' if system=='sga-cd' else '/')
   context=self.unwrap(client.get(route,params=query))['context']
   body=contracts['sample'](system,context['tenant_ref'],context['actor_ref'],version='1.1',kind='CAPABILITY_PLAN')
   body['expires_at']=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
   capabilities=self.unwrap(client.get(route,params=query))['capabilities']
   body['task_graph']=[{'id':str(uuid4()),'capability':row['id'],'depends_on':[]} for row in capabilities]
   url=prefix+'intents/validate'+('' if system=='sga-cd' else '/')
   result=self.unwrap(client.post(url,params=query,json=body,headers={'X-POOL08-Contract-Version':'1.1'}))
   self.assertEqual(result['schema_version'],'1.1');self.assertEqual(len(result['planned_tasks']),20)
   self.assertTrue(all(row['state']=='REQUIRES_DOMAIN_BINDING' and row['execution_enabled'] is False for row in result['planned_tasks']))
 def test_contract_errors_have_equal_http_codes_and_safe_error_header(self):
  for system,client,query,prefix in self.targets():
   route=prefix+'capabilities'+('' if system=='sga-cd' else '/')
   context=self.unwrap(client.get(route,params=query))['context']
   url=prefix+'intents/validate'+('' if system=='sga-cd' else '/')
   body=contracts['sample'](system,context['tenant_ref'],context['actor_ref'],version='1.1',kind='CAPABILITY_PLAN');body['expires_at']=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
   for raw,code,status in [(b'{"x":1,"x":2}','DUPLICATE_FIELD',400),(b' '*17000,'BODY_LIMIT',413)]:
    response=client.post(url,params=query,content=raw,headers={'content-type':'application/json'})
    self.assertEqual(response.status_code,status,response.text);self.assertEqual(response.headers['x-pool08-error-code'],code)
   for key,value,code,status in [('tenant_ref','foreign','CONTEXT_MISMATCH',403),('schema_version','9.0','UNSUPPORTED_VERSION',409),('intent_kind','INVALID','SCHEMA_INVALID',422)]:
    invalid=dict(body);invalid[key]=value;response=client.post(url,params=query,json=invalid)
    self.assertEqual(response.status_code,status,response.text);self.assertEqual(response.headers['x-pool08-error-code'],code)
 def test_header_cannot_silently_upgrade_or_downgrade_body_version(self):
  for system,client,query,prefix in self.targets():
   route=prefix+'capabilities'+('' if system=='sga-cd' else '/')
   context=self.unwrap(client.get(route,params=query))['context']
   body=contracts['sample'](system,context['tenant_ref'],context['actor_ref']);body['expires_at']=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
   url=prefix+'intents/validate'+('' if system=='sga-cd' else '/')
   response=client.post(url,params=query,json=body,headers={'X-POOL08-Contract-Version':'1.1'})
   self.assertEqual(response.status_code,409,response.text);self.assertEqual(response.headers['x-pool08-error-code'],'CONTRACT_VERSION_MISMATCH')
 def test_gateway_uses_native_authority_and_no_legacy_sga_fallback(self):
  client,cred=self.extra['gateway'];prefix='/api/v1/commercial-unified/';query={'provider_id':cred['provider_id']}
  catalog=self.unwrap(client.get(prefix+'capabilities',params=query));self.assertEqual(catalog['system'],'analematica')
  self.assertEqual(client.get(prefix+'capabilities',params=query,headers={'Authorization':''}).status_code,401)
  self.assertEqual(client.get(prefix+'capabilities',params=query,headers={'Authorization':'Bearer '+cred['other_token']}).status_code,403)
  self.assertEqual(client.get(prefix+'arbitrary/path',params=query).status_code,404)
  self.assertEqual(client.delete(prefix+'contract',params=query).status_code,405)
 def test_same_draft_through_native_and_gateway_returns_same_fingerprint(self):
  native,cred=self.servers['analematica'];gateway=self.extra['gateway'][0];query={'provider_id':cred['provider_id']};prefix='/api/v1/commercial-unified/'
  context=self.unwrap(native.get(prefix+'capabilities/',params=query))['context']
  body=contracts['sample']('analematica',context['tenant_ref'],context['actor_ref'],version='1.1');body['expires_at']=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat()
  original=self.unwrap(native.post(prefix+'intents/validate/',params=query,json=body));forwarded=self.unwrap(gateway.post(prefix+'intents/validate',params=query,json=body))
  self.assertEqual(original,forwarded);self.assertFalse(forwarded['payment_verified']);self.assertFalse(forwarded['execution_authorized'])

if __name__=='__main__':unittest.main(verbosity=2)
