"""Opaque package shape and customer API boundaries. SQL is tested separately on PostgreSQL."""
import base64,copy,hashlib,json,secrets,sys,tempfile,unittest,uuid
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime,timedelta,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'ANALEMATICA-BACKEND'))
from core_erp.accounting.customer_package_store import inspect_package
from core_erp.accounting.customer_package_api import build_app
from fastapi.testclient import TestClient

def package(company,document=None,revision=1,previous=None):
 e=lambda b:base64.urlsafe_b64encode(b).rstrip(b'=').decode()
 value={'schema':'sgacd-fiscal-package-v1','revision':revision,'previous_digest':previous,'key_descriptor':{'kdf':'PBKDF2-SHA256','iterations':600000,'salt':e(b's'*16)},'envelope':{'schema':'sgacd-fiscal-envelope-v1','algorithm':'AES-256-GCM+A256KW','context':{'company_id':str(company),'document_id':str(document or uuid.uuid4())},'iv':e(b'i'*12),'wrapped_key':e(b'w'*40),'ciphertext':e(b'opaque-test-ciphertext-1234')},'auth_tag':e(b't'*32)}
 value['package_digest']=hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest();return value

class CustomerPackageChecks(unittest.TestCase):
 def setUp(self):
  self.company=str(uuid.uuid4());self.value=package(self.company);self.private=tempfile.TemporaryDirectory();self.addCleanup(self.private.cleanup);self.path=Path(self.private.name)/'grant.json';self.token='byos_'+secrets.token_urlsafe(32);self.moment=datetime.now(timezone.utc);self.grant={'company_id':self.company,'token_sha256':hashlib.sha256(self.token.encode()).hexdigest(),'expires_at':(self.moment+timedelta(hours=1)).isoformat(),'permissions':['read','append'],'allowed_origins':['https://frontend.example.test']};self.save_grant()
  class MemoryStore:
   company_id=self.company
   def __init__(store):store.items={}
   def put(store,v):r,_=inspect_package(v,store.company_id);store.items[r['document_id']]=copy.deepcopy(v);return {**r,'stored':True,'authenticated_ciphertext_verified':False,'fiscal_accepted':False,'ledger_written':False}
   def get(store,doc,revision=None):
    if doc not in store.items:raise LookupError()
    return store.items[doc]
  self.store=MemoryStore()
  @contextmanager
  def factory():yield self.store
  self.client=TestClient(build_app(factory,self.path,clock=lambda:self.moment));self.addCleanup(self.client.close);self.headers={'Authorization':'Bearer '+self.token,'Origin':'https://frontend.example.test'}
 def save_grant(self):self.path.write_text(json.dumps(self.grant));self.path.chmod(0o600)
 def post(self,**extra):return self.client.post('/v1/packages',json=self.value,headers={**self.headers,**extra})
 def test_shape_digest_and_scope(self):
  r,encoded=inspect_package(self.value,self.company);self.assertEqual(r['package_digest'],self.value['package_digest']);self.assertEqual(json.loads(encoded),self.value)
  with self.assertRaises(ValueError):inspect_package(self.value,uuid.uuid4())
 def test_rejects_unknown_fields_bool_revision_and_bad_kdf(self):
  for changes in [{'plaintext':'forbidden'},{'revision':True},{'revision':0},{'revision':2},{'key_descriptor':{**self.value['key_descriptor'],'iterations':600000.0}},{'key_descriptor':{**self.value['key_descriptor'],'salt':'invalid='}},{'auth_tag':'invalid'},{'package_digest':'a'*64}]:
   with self.subTest(changes=changes):
    with self.assertRaises(ValueError):inspect_package({**self.value,**changes},self.company)
 def test_private_identity_and_opaque_roundtrip(self):
  r=self.client.get('/v1/identity',headers=self.headers);self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['authenticated_ciphertext_verified']);self.assertIn('no-store',r.headers['cache-control']);r=self.post();self.assertEqual(r.status_code,200,r.text);self.assertFalse(r.json()['fiscal_accepted']);doc=self.value['envelope']['context']['document_id'];self.assertEqual(self.client.get('/v1/packages/'+doc,headers=self.headers).json(),self.value)
 def test_wrong_or_absent_bearer_rejected(self):
  self.assertEqual(self.client.get('/v1/identity').status_code,401);self.assertEqual(self.post(Authorization='Bearer '+'x'*40).status_code,401);self.assertFalse(self.store.items)
 def test_permission_revoked_per_request(self):
  self.grant['permissions']=['read'];self.save_grant();self.assertEqual(self.post().status_code,403);self.assertEqual(self.client.get('/v1/identity',headers=self.headers).status_code,200)
 def test_token_revoked_and_expired_per_request(self):
  self.grant['token_sha256']='a'*64;self.save_grant();self.assertEqual(self.post().status_code,401);self.grant['token_sha256']=hashlib.sha256(self.token.encode()).hexdigest();self.grant['expires_at']=(self.moment-timedelta(seconds=1)).isoformat();self.save_grant();self.assertEqual(self.post().status_code,401)
 def test_foreign_origin_denied(self):self.assertEqual(self.post(Origin='https://untrusted.example.test').status_code,403);self.assertFalse(self.store.items)
 def test_grant_company_cannot_select_other_store(self):
  self.grant['company_id']=str(uuid.uuid4());self.save_grant();self.assertEqual(self.post().status_code,400);self.assertFalse(self.store.items)
 def test_duplicate_keys_and_nonfinite_json_denied(self):
  for raw in [b'{"schema":1,"schema":2}',b'{"value":NaN}',b'{"value":Infinity}']:
   r=self.client.post('/v1/packages',content=raw,headers={**self.headers,'Content-Type':'application/json'});self.assertEqual(r.status_code,400,r.text)
 def test_oversize_and_compressed_body_denied(self):
  r=self.client.post('/v1/packages',content=b'x'*1500001,headers={**self.headers,'Content-Type':'application/json'});self.assertEqual(r.status_code,413);self.assertEqual(self.post(**{'Content-Encoding':'gzip'}).status_code,415);self.assertFalse(self.store.items)
 def test_bad_package_and_not_found(self):
  self.value['package_digest']='0'*64;self.assertEqual(self.post().status_code,400);self.assertEqual(self.client.get('/v1/packages/'+str(uuid.uuid4()),headers=self.headers).status_code,404)
 def test_public_grant_file_refused(self):
  self.path.chmod(0o644);self.assertEqual(self.post().status_code,503)
 def test_customer_api_has_no_public_documentation(self):self.assertEqual(self.client.get('/docs').status_code,404);self.assertEqual(self.client.get('/openapi.json').status_code,404)
 def test_cors_only_explicit_origin_no_credentials(self):
  h={'Origin':'https://frontend.example.test','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'Authorization,Content-Type'};r=self.client.options('/v1/packages',headers=h);self.assertEqual(r.status_code,200);self.assertEqual(r.headers['access-control-allow-origin'],h['Origin']);self.assertNotIn('access-control-allow-credentials',r.headers);r=self.client.options('/v1/packages',headers={**h,'Origin':'https://untrusted.example.test'});self.assertEqual(r.status_code,400)
 def test_standalone_startup_does_not_connect_or_initialize_storage(self):
  import os
  from unittest.mock import patch
  from core_erp.accounting.customer_package_api import create_app
  config=Path(self.private.name)/'deployment.json';config.write_text(json.dumps({'company_id':self.company,'grant_file':str(self.path),'database':{'ENGINE':'django.db.backends.postgresql','NAME':'not-connected','HOST':'invalid.example.test','USER':'not-real','PASSWORD':'not-real'}}));config.chmod(0o600)
  with patch.dict(os.environ,{'CUSTOMER_PACKAGE_CONFIG':str(config)}):
   app=create_app()
   with TestClient(app) as client:self.assertEqual(client.get('/v1/identity').status_code,401)
if __name__=='__main__':unittest.main()
