"""SGA-CD FastAPI commercial contract, real identity/plan queries, isolated SQLite."""
import runpy,unittest,json,os
from uuid import uuid4
from pathlib import Path
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[3]
fixtures=runpy.run_path(str(Path(__file__).resolve().parents[3] / 'BACKEND/tests/workspace/test_workspace.py'),run_name='pool08_sga_fixture')
contracts=runpy.run_path(str(ROOT/'BACKEND/deployment/tests/pool08_contract_check.py'),run_name='pool08_contract_fixture')
from app.commercial.pool08.api import router
from app.models.workspace import WorkspaceLead
class SGAPool08Checks(unittest.TestCase):
 def setUp(self):
  fixtures['WorkspaceTests'].setUp(self)
  self.client.app.include_router(router,prefix='/api/v1/commercial-unified')
 tearDown=fixtures['WorkspaceTests'].tearDown
 login=fixtures['WorkspaceTests'].login
 def draft(self):
  response=self.client.get('/api/v1/commercial-unified/capabilities');self.assertEqual(response.status_code,200,response.text);context=response.json()['context']
  body=contracts['sample']('sga-cd',context['tenant_ref'],context['actor_ref']);body['expires_at']=(datetime.now(timezone.utc)+timedelta(minutes=5)).isoformat();return body
 def test_catalog_and_draft_do_not_create_or_execute_a_sale(self):
  before=self.db.query(WorkspaceLead).count();response=self.client.post('/api/v1/commercial-unified/intents/validate',json=self.draft())
  self.assertEqual(response.status_code,200,response.text);self.assertFalse(response.json()['execution_authorized']);self.assertFalse(response.json()['payment_verified']);self.assertEqual(response.headers['cache-control'],'no-store');self.assertEqual(self.db.query(WorkspaceLead).count(),before)
 def test_anonymous_and_basic_plan_rejected(self):
  self.client.headers.pop('Authorization');self.assertEqual(self.client.get('/api/v1/commercial-unified/capabilities').status_code,401)
  self.login('basic-admin_empresa');self.assertEqual(self.client.get('/api/v1/commercial-unified/capabilities').status_code,402)
 def test_employee_without_crm_permission_rejected(self):
  self.login('full-jefe_area');self.assertEqual(self.client.get('/api/v1/commercial-unified/capabilities').status_code,403)
 def test_company_and_actor_cannot_be_forged(self):
  body=self.draft();body['tenant_ref']='tenant:foreign';response=self.client.post('/api/v1/commercial-unified/intents/validate',json=body)
  self.assertEqual(response.status_code,403);self.assertEqual(response.json()['detail']['code'],'CONTEXT_MISMATCH')
 def test_duplicate_json_and_large_body_are_bounded(self):
  for raw,status in [('{'+'"x":1,"x":2}',400),(' '*17000,413)]:
   response=self.client.post('/api/v1/commercial-unified/intents/validate',content=raw,headers={'content-type':'application/json'});self.assertEqual(response.status_code,status);self.assertEqual(response.headers['cache-control'],'no-store')
 def test_analematica_gateway_does_not_impersonate_sga_commercial_contract(self):
  import importlib.util
  from fastapi.testclient import TestClient
  spec=importlib.util.spec_from_file_location('pool08_ana_gateway',ROOT/'BACKEND/ANALEMATICA-BACKEND/deployment/api.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  with TestClient(module.app) as client:
   response=client.get('/api/v1/commercial-unified/capabilities');self.assertEqual(response.status_code,503);self.assertFalse(response.json()['execution_authorized']);self.assertEqual(response.json()['code'],'NATIVE_COMMERCIAL_ROUTE_REQUIRED')

class GatewayBoundaryChecks(unittest.TestCase):
 def setUp(self):
  import importlib.util
  from pathlib import Path
  from fastapi.testclient import TestClient
  root=Path(__file__).resolve().parents[3]
  self.env=patch.dict(os.environ,{'ANALEMATICA_COMMERCIAL_API_URL':''});self.env.start();self.addCleanup(self.env.stop)
  spec=importlib.util.spec_from_file_location('gc001_gateway_'+str(uuid4()),root/'BACKEND/ANALEMATICA-BACKEND/deployment/api.py')
  self.module=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.module)
  self.client=TestClient(self.module.app);self.client.__enter__();self.addCleanup(self.client.__exit__,None,None,None)
 def native(self,handler):
  import httpx
  native=httpx.AsyncClient(base_url='http://localhost:9998',transport=httpx.MockTransport(handler),follow_redirects=False,trust_env=False)
  self.client.app.state.commercial_upstream=native;self.addCleanup(self.client.portal.call,native.aclose)
 def test_unconfigured_channel_is_explicit_and_does_not_use_legacy_backend(self):
  response=self.client.get('/api/v1/commercial-unified/contract')
  self.assertEqual(response.status_code,503);self.assertEqual(response.json()['code'],'NATIVE_COMMERCIAL_ROUTE_REQUIRED')
 def test_native_origin_is_internal_fixed_and_validated(self):
  self.assertEqual(self.module.commercial_origin('http://localhost:8000/'),'http://localhost:8000')
  for origin in ('https://example.org','http://localhost:70000','http://user:password@localhost','http://localhost/path','http://localhost?token=private','http://localhost#fragment','http://localhost\n'):
   with self.assertRaises(ValueError):self.module.commercial_origin(origin)
 def test_redirects_are_not_followed_and_body_limit_is_enforced(self):
  import httpx
  seen=[]
  def handler(request):seen.append(request);return httpx.Response(302,headers={'Location':'https://not-contacted.example/'})
  self.native(handler)
  response=self.client.get('/api/v1/commercial-unified/contract');self.assertEqual(response.status_code,502);self.assertEqual(len(seen),1)
  response=self.client.post('/api/v1/commercial-unified/intents/validate',content=' '*17000,headers={'content-type':'application/json'})
  self.assertEqual(response.status_code,413);self.assertEqual(len(seen),1)
 def test_upstream_error_does_not_fall_back_to_sga(self):
  import httpx
  calls=[]
  def handler(request):calls.append(request);raise httpx.ConnectError('isolated unavailable native',request=request)
  self.native(handler);response=self.client.get('/api/v1/commercial-unified/capabilities')
  self.assertEqual(response.status_code,503);self.assertEqual(response.json()['code'],'NATIVE_COMMERCIAL_UNAVAILABLE');self.assertEqual(len(calls),1)
 def test_response_limit_and_route_allowlist(self):
  import httpx
  calls=[]
  def handler(request):calls.append(request);return httpx.Response(200,content=b'x'*524289)
  self.native(handler);self.assertEqual(self.client.get('/api/v1/commercial-unified/contract').status_code,502)
  self.assertEqual(self.client.get('/api/v1/commercial-unified/arbitrary').status_code,404)
  self.assertEqual(self.client.delete('/api/v1/commercial-unified/capabilities').status_code,405);self.assertEqual(len(calls),1)
 def test_each_request_has_explicit_auth_and_cookie_and_no_host_or_tenant_override(self):
  import httpx
  calls=[]
  def handler(request):
   calls.append(request)
   return httpx.Response(200,json={'schema_version':'1.1','system':'analematica'},headers={'Set-Cookie':'private_fixture_session=one; Path=/','X-POOL08-Contract-Version':'1.1'})
  self.native(handler)
  first=self.client.get('/api/v1/commercial-unified/contract?provider_id=fixture',headers={'Authorization':'Bearer fixture-A','Cookie':'caller_session=A','Host':'untrusted-caller.example','X-Tenant-ID':'forged','X-POOL08-Contract-Version':'1.1'})
  second=self.client.get('/api/v1/commercial-unified/contract',headers={'Authorization':'Bearer fixture-B','Cookie':''})
  self.assertEqual(first.status_code,200);self.assertEqual(second.status_code,200)
  self.assertEqual(calls[0].headers['authorization'],'Bearer fixture-A');self.assertEqual(calls[1].headers['authorization'],'Bearer fixture-B')
  self.assertEqual(calls[0].headers['cookie'],'caller_session=A');self.assertEqual(calls[1].headers['cookie'],'')
  self.assertEqual(calls[0].headers['host'],'localhost:9998');self.assertNotIn('x-tenant-id',calls[0].headers)
  self.assertEqual(calls[0].url.path,'/api/v1/commercial-unified/contract/');self.assertEqual(calls[0].url.query,b'provider_id=fixture')
  self.assertEqual(first.headers['x-pool08-contract-version'],'1.1');self.assertEqual(first.headers['cache-control'],'no-store')

if __name__=='__main__':unittest.main(verbosity=2)
