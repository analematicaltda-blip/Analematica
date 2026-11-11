"""Mocked provider contracts only: not real OAuth grants or ownership qualification."""
import sys,unittest,uuid,json,copy,hashlib,base64
from pathlib import Path
from urllib.parse import urlsplit,parse_qs,urlencode
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT/'DESKTOP/customer-cloud-store'),str(ROOT/'DESKTOP/fiscal-signer')]
import httpx
from oauth_client import NativeOAuth,AccessSession,OAuthError,PROVIDERS
from cloud_store import CloudStore,Destination,CloudError,CloudConflict,UploadOutcomeUnknown
from package_crypto import seal_package

class OAuthContracts(unittest.TestCase):
 def make(self,provider='google_drive',handler=None):
  self.now=100;self.calls=[]
  def exchange(req):
   self.calls.append(req)
   if handler:return handler(req)
   return httpx.Response(200,json={'access_token':'synthetic-token-for-mock-only','expires_in':120,'token_type':'Bearer','scope':PROVIDERS[provider]['scope']})
  return NativeOAuth(provider,'synthetic-client-123','http://127.0.0.1:19876/oauth/callback',client=httpx.Client(transport=httpx.MockTransport(exchange)),clock=lambda:self.now)
 def callback(self,oauth):
  q=parse_qs(urlsplit(oauth.begin()).query);return oauth.redirect_uri+'?'+urlencode({'code':'synthetic-code','state':q['state'][0]}),q
 def test_pkce_and_minimal_scopes_both_providers(self):
  for provider in PROVIDERS:
   oauth=self.make(provider);callback,q=self.callback(oauth);session=oauth.finish(callback);posted=parse_qs(self.calls[0].content.decode())
   challenge=base64.urlsafe_b64encode(hashlib.sha256(posted['code_verifier'][0].encode()).digest()).rstrip(b'=').decode()
   self.assertEqual(q['code_challenge'],[challenge]);self.assertEqual(q['code_challenge_method'],['S256']);self.assertEqual(q['scope'],[PROVIDERS[provider]['scope']]);self.assertNotIn('client_secret',posted);self.assertNotIn('synthetic-token',repr(session))
 def test_state_destination_duplicates_and_replay(self):
  oauth=self.make();callback,_=self.callback(oauth)
  for bad in [callback.replace('127.0.0.1','localhost'),callback+'&state=duplicate',callback.replace('state=','state=bad')]:
   with self.assertRaises(OAuthError):oauth.finish(bad)
  self.assertEqual(len(self.calls),0);oauth.finish(callback)
  with self.assertRaises(OAuthError):oauth.finish(callback)
 def test_expiration_and_forget(self):
  oauth=self.make();callback,_=self.callback(oauth);self.now+=301
  with self.assertRaises(OAuthError):oauth.finish(callback)
  session=AccessSession('google_drive','not-a-real-token',101,lambda:self.now)
  with self.assertRaises(OAuthError):session.bearer()
  session.forget();self.assertEqual(session._token,'')
 def test_excess_scope_rejected(self):
  oauth=self.make(handler=lambda r:httpx.Response(200,json={'access_token':'synthetic-token-for-mock-only','expires_in':120,'token_type':'Bearer','scope':'https://www.googleapis.com/auth/drive'}));callback,_=self.callback(oauth)
  with self.assertRaises(OAuthError):oauth.finish(callback)
 def test_exchange_timeout_consumes_code(self):
  def fail(r):raise httpx.ReadTimeout('mock timeout',request=r)
  oauth=self.make(handler=fail);callback,_=self.callback(oauth)
  with self.assertRaises(OAuthError):oauth.finish(callback)
  with self.assertRaises(OAuthError):oauth.finish(callback)
  self.assertEqual(len(self.calls),1)
 def test_unregistered_callback_and_provider_rejected(self):
  for provider,redirect in [('other','http://127.0.0.1:19876/oauth/callback'),('google_drive','https://attacker.example/oauth/callback')]:
   with self.assertRaises(OAuthError):NativeOAuth(provider,'synthetic-client-123',redirect)

 def test_response_size_and_redirect_refused(self):
  for response in [httpx.Response(302,headers={'Location':'https://attacker.example/'}),httpx.Response(200,content=b'x'*65537)]:
   oauth=self.make(handler=lambda r,response=response:response);callback,_=self.callback(oauth)
   with self.assertRaises(OAuthError):oauth.finish(callback)
   self.assertEqual(len(self.calls),1)

class CloudContracts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.scope={'company_id':str(uuid.uuid4()),'document_id':str(uuid.uuid4())};cls.package=seal_package(b'<Invoice>private mock</Invoice>','synthetic password for tests',cls.scope)
 def make(self,provider):
  self.stored=False;self.requests=[];self.writes=0;self.failure=None;self.corrupt=False;self.host='download.customer.example';self.status=None
  def handler(req):
   self.requests.append(req);p=req.url.path
   if self.status:return httpx.Response(self.status,json={'error':'sensitive provider body must not echo'})
   if req.url.host==self.host:
    self.assertNotIn('authorization',req.headers);self.assertNotIn('cookie',req.headers)
    return httpx.Response(200,content=self.raw if not self.corrupt else b'corrupted')
   self.assertEqual(req.headers.get('authorization'),'Bearer synthetic-access-token-for-mock')
   if p=='/drive/v3/about':return httpx.Response(200,json={'user':{'permissionId':'account123'}})
   if p=='/drive/v3/files/root123':return httpx.Response(200,json={'id':'root123','mimeType':'application/vnd.google-apps.folder','ownedByMe':True,'trashed':False})
   if p=='/v1.0/me/drive/special/approot':return httpx.Response(200,json={'id':'root123','parentReference':{'driveId':'account123'},'folder':{}})
   if p=='/drive/v3/files/generateIds':return httpx.Response(200,json={'ids':['allocated-file-12345']})
   if req.method in {'POST','PUT'}:
    self.writes+=1;self.stored=True
    self.assertNotIn(b'<Invoice>',req.content);self.assertNotIn(b'synthetic password',req.content)
    if provider=='onedrive':self.assertEqual(req.headers['if-none-match'],'*');self.assertEqual(req.url.params['@microsoft.graph.conflictBehavior'],'fail')
    if self.failure=='timeout':raise httpx.ReadTimeout('mock response lost',request=req)
    if self.failure=='500':return httpx.Response(500)
    return httpx.Response(201,json={'id':'allocated-file-12345'})
   if not self.stored:return httpx.Response(404)
   if provider=='google_drive':
    if req.url.params.get('alt')=='media':return httpx.Response(200,content=self.raw if not self.corrupt else b'corrupted')
    return httpx.Response(200,json={'id':self.plan['file_id'],'name':self.plan['name'],'parents':['root123'],'ownedByMe':True,'trashed':False,'appProperties':{'sgacd_blob_sha256':self.plan['blob_sha256'],'sgacd_company_id':self.scope['company_id']}})
   return httpx.Response(200,json={'name':self.plan['name'],'parentReference':{'id':'root123','driveId':'account123'},'file':{},'size':len(self.raw),'@microsoft.graph.downloadUrl':'https://'+self.host+'/opaque?secret=mock-download'})
  destination=Destination(provider,self.scope['company_id'],'account123','root123',('download.customer.example',))
  session=AccessSession(provider,'synthetic-access-token-for-mock',999999999999)
  self.store=CloudStore(destination,session,client=httpx.Client(transport=httpx.MockTransport(handler),headers={'Cookie':'should-not-leak-to-download=1'}))
  self.raw=self.store.checked_package(self.package)[1];self.plan=self.store.prepare(self.package);return self.store
 def test_upload_readback_and_replay_both_providers(self):
  for provider in PROVIDERS:
   store=self.make(provider);receipt=store.put(self.package,self.plan,confirmed=True);self.assertTrue(receipt['stored']);self.assertFalse(receipt['provider_live_qualified']);self.assertFalse(receipt['authenticated_ciphertext_verified']);self.assertTrue(store.put(self.package,self.plan,confirmed=True)['replayed']);self.assertEqual(self.writes,1);self.assertNotIn('token',json.dumps(self.plan))
 def test_uncertain_result_recovers_without_second_write(self):
  for provider in PROVIDERS:
   for failure in ['timeout','500']:
    store=self.make(provider);self.failure=failure
    with self.assertRaises(UploadOutcomeUnknown) as error:store.put(self.package,self.plan,confirmed=True)
    self.assertEqual(error.exception.plan,self.plan);self.failure=None;self.assertTrue(store.put(self.package,self.plan,confirmed=True)['replayed']);self.assertEqual(self.writes,1)
 def test_revoked_and_forbidden_do_not_acknowledge(self):
  for status in [401,403]:
   store=self.make('google_drive');self.status=status
   with self.assertRaises(CloudError) as error:store.put(self.package,self.plan,confirmed=True)
   self.assertNotIn('sensitive',str(error.exception));self.assertEqual(self.writes,0);self.assertEqual(store.session.revoked,status==401)
 def test_conflicting_bytes_never_overwritten(self):
  for provider in PROVIDERS:
   store=self.make(provider);self.stored=True;self.corrupt=True
   with self.assertRaises(CloudConflict):store.put(self.package,self.plan,confirmed=True)
   self.assertEqual(self.writes,0)
 def test_scope_plan_or_bytes_tampering(self):
  store=self.make('google_drive')
  for key,val in [('company_id',str(uuid.uuid4())),('root_id','other123'),('account_id','other123'),('blob_sha256','a'*64)]:
   plan={**self.plan,key:val}
   with self.assertRaises(CloudConflict):store.put(self.package,plan,confirmed=True)
  self.assertEqual(self.writes,0)
 def test_confirmation_required(self):
  store=self.make('google_drive')
  with self.assertRaises(CloudError):store.put(self.package,self.plan)
  self.assertEqual(self.writes,0)
 def test_unapproved_download_host_rejected(self):
  store=self.make('onedrive');self.stored=True;self.host='attacker.example'
  with self.assertRaises(CloudError):store.recover(self.package,self.plan)
  self.assertFalse(any(r.url.host=='attacker.example' for r in self.requests))
 def test_session_provider_mismatch(self):
  with self.assertRaises(CloudError):CloudStore(Destination('onedrive',self.scope['company_id'],'account123','root123'),AccessSession('google_drive','synthetic',9999999999))

 def test_wrong_customer_root_stops_before_upload(self):
  store=self.make('google_drive');store.destination=Destination('google_drive',self.scope['company_id'],'other-account','root123')
  with self.assertRaises(CloudError):store.verify_destination()
  self.assertEqual(self.writes,0)
 def test_no_redirect_chains_in_anonymous_download(self):
  store=self.make('onedrive');self.stored=True
  original=store.client
  def redirect(req):return httpx.Response(302,headers={'Location':'https://attacker.example/'}) if req.url.host==self.host else original.send(req)
  store.client=httpx.Client(transport=httpx.MockTransport(redirect))
  with self.assertRaises(CloudError):store.recover(self.package,self.plan)
  self.assertEqual(self.writes,0)

if __name__=='__main__':unittest.main(verbosity=2)
