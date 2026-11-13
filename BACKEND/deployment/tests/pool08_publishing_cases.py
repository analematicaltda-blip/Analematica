"""Publication calendar checks against the three real private ORM adapters."""
import importlib,uuid,copy,json,os,httpx
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
from pool08_mobile_message_cases import MobileCases
class PublishingCases:
 def setup_publish(self):
  self.module=importlib.import_module(self.module_path+'.publishing');store=importlib.import_module(self.module_path+'.publishing_store');self.now=datetime.now(timezone.utc);self.pub=self.module.Publishing(store.Store(self.gen.crm.store),self.gen.crm,clock=lambda:self.now)
  self.profile={'version':'fixture-1','format':'FACEBOOK_PHOTO','account_id':'123','page_id':'','credential_env':'COMMERCIAL_PUBLISH_SECRET_TEST','public_base_url':'https://media.example.test','allow_publish':True,'ownership_support_digest':'a'*64,'daily_limit':10};env=patch.dict(os.environ,{'COMMERCIAL_PUBLISH_ACCOUNTS':json.dumps({self.pub.key():{'owned-page-fixture':self.profile}}),'COMMERCIAL_PUBLISH_WORKER_ENABLED':'1','COMMERCIAL_PUBLISH_NETWORK_ENABLED':'1','COMMERCIAL_PUBLISH_SECRET_TEST':'fixture-not-real-token-12345'});env.start();self.addCleanup(env.stop)
 def asset(self):return MobileCases.media(self)
 def body(self,op='create',ref=None,revision=0,**data):
  if op=='create':data={'title':'Calendario sintético','caption':'Contenido de laboratorio','format':'FACEBOOK_PHOTO','account_ref':'owned-page-fixture','visibility':'PUBLIC','disclosure':'NONE','media_ref':self.asset(),**data}
  return {'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':revision,'data':data}
 def create_pub(self):return self.pub.command(self.body())['job_id']
 def schedule(self,ref,delay=60):
  self.pub.command(self.body('review',ref,1,confirmed_content=True,confirmed_account=True));return self.pub.command(self.body('schedule',ref,2,confirmed_impact=True,scheduled_at=(self.now+timedelta(seconds=delay)).isoformat()))
 def test_draft_replay_and_conflicting_request(self):
  self.setup_publish();body=self.body();receipt=self.pub.command(body);self.assertEqual(receipt['status'],'DRAFT');self.assertTrue(self.pub.command(body)['replayed']);self.assertEqual(self.pub.receipt(body['request_id'])['job_id'],receipt['job_id']);body['data']['caption']='Cambio'
  with self.assertRaises(self.error):self.pub.command(body)
 def test_two_reviews_and_schedule_do_not_publish(self):
  self.setup_publish();ref=self.create_pub()
  with self.assertRaises(self.error):self.pub.command(self.body('schedule',ref,1,confirmed_impact=True,scheduled_at=self.now.isoformat()))
  self.schedule(ref);d=self.pub.get(ref);self.assertEqual(d['status'],'SCHEDULED');self.assertNotEqual(d['review']['request_id'],d['authorization']['request_id']);self.assertEqual(d['attempts'],0);self.assertIsNone(d['published_at']);self.assertFalse(d['account_ownership_verified']);self.assertFalse(self.pub.list()['saving_publishes'])
 def test_due_calendar_normalizes_timezone_and_filters_before_limit(self):
  self.setup_publish();future=self.create_pub();self.schedule(future,3600);due=self.create_pub();self.schedule(due,1);self.now+=timedelta(seconds=2);self.assertEqual([j['id'] for j in self.pub.due(1)],[due]);self.assertEqual(self.pub.due(1)[0]['scheduled_at'][-6:],'+00:00')
 def test_cancelled_job_is_not_due_and_cannot_reschedule(self):
  self.setup_publish();ref=self.create_pub();self.schedule(ref,1);self.pub.command(self.body('cancel',ref,3));self.now+=timedelta(seconds=2);self.assertEqual(self.pub.due(),[])
  with self.assertRaises(self.error):self.pub.command(self.body('schedule',ref,4,confirmed_impact=True,scheduled_at=self.now.isoformat()))
 def test_past_far_future_and_naive_times_rejected(self):
  self.setup_publish();ref=self.create_pub();self.pub.command(self.body('review',ref,1,confirmed_content=True,confirmed_account=True))
  for when in [self.now-timedelta(seconds=1),self.now+timedelta(days=31),self.now.replace(tzinfo=None)]:
   with self.assertRaises(self.error):self.pub.command(self.body('schedule',ref,2,confirmed_impact=True,scheduled_at=when.isoformat()))
  self.assertEqual(self.pub.get(ref)['revision'],2)
 def test_withdrawn_media_cannot_be_scheduled(self):
  self.setup_publish();ref=self.create_pub();d=self.pub.get(ref);lib=importlib.import_module(self.module_path+'.library_api').service(self.gen.crm);lib.command({'request_id':str(uuid.uuid4()),'operation':'withdraw','item_id':d['media_ref']['item_id'],'expected_revision':3,'data':{'confirmed':True}})
  with self.assertRaises(self.error):self.pub.command(self.body('review',ref,1,confirmed_content=True,confirmed_account=True))
  self.assertEqual(self.pub.get(ref)['status'],'DRAFT')
 def test_role_revocation_blocks_get_command_history_and_receipt(self):
  self.setup_publish();body=self.body();ref=self.pub.command(body)['job_id']
  with patch.object(self.gen.crm,'authorize',side_effect=self.error('TEST_REVOKED',403)):
   for action in [lambda:self.pub.get(ref),lambda:self.pub.history(ref),lambda:self.pub.receipt(body['request_id']),lambda:self.pub.command(self.body('cancel',ref,1)),lambda:self.pub.due()]:
    with self.assertRaises(self.error):action()
 def test_stale_revision_and_false_confirmation_do_not_mutate(self):
  self.setup_publish();ref=self.create_pub()
  for data,rev in [({'confirmed_content':True,'confirmed_account':False},1),({'confirmed_content':1,'confirmed_account':True},1),({'confirmed_content':True,'confirmed_account':True},0)]:
   with self.assertRaises(self.error):self.pub.command(self.body('review',ref,rev,**data))
  self.assertEqual(self.pub.get(ref)['revision'],1)
 def mock_client(self,mode='normal'):
  self.requests=[]
  def send(req):
   self.requests.append(req)
   if req.url.path.endswith('/me'):return httpx.Response(200,json={'id':'123'})
   if req.method=='POST':
    if mode=='timeout':raise httpx.ReadTimeout('synthetic',request=req)
    return httpx.Response(200,json={} if mode=='generic' else {'id':'456','post_id':'123_456'})
   return httpx.Response(200,json={'id':'123_456','from':{'id':'123'},'is_published':mode!='unconfirmed'})
  def factory(**kwargs):
   self.assertFalse(kwargs['follow_redirects']);self.assertFalse(kwargs['trust_env']);return httpx.Client(transport=httpx.MockTransport(send),**kwargs)
  return factory
 def test_upload_ack_is_not_publication_and_second_step_reads_only(self):
  self.setup_publish();ref=self.create_pub();self.schedule(ref,1);self.now+=timedelta(seconds=2);factory=self.mock_client();self.pub.dispatch(ref,client_factory=factory);d=self.pub.get(ref);self.assertEqual(d['status'],'VERIFY');self.assertIsNone(d['published_at']);self.assertEqual(d['remote_id'],'123_456');self.now+=timedelta(seconds=31);self.pub.dispatch(ref,client_factory=factory);d=self.pub.get(ref);self.assertEqual(d['status'],'PUBLISHED');self.assertEqual(d['remote_proof']['basis'],'PROVIDER_READ');self.assertEqual(sum(v.method=='POST' for v in self.requests),1);self.assertFalse(d['live_adapter_qualified'])
 def test_timeout_or_generic_200_never_reuploads(self):
  self.setup_publish()
  for mode in ['timeout','generic']:
   ref=self.create_pub();self.schedule(ref,1);self.now+=timedelta(seconds=2);self.pub.dispatch(ref,client_factory=self.mock_client(mode));self.assertEqual(self.pub.get(ref)['status'],'UNCERTAIN')
   with self.assertRaises(self.error):self.pub.dispatch(ref,client_factory=self.mock_client())
 def test_interrupted_mutation_recovers_uncertain_without_retry(self):
  self.setup_publish();ref=self.create_pub();self.schedule(ref,1);self.now+=timedelta(seconds=2);self.pub.claim(ref);self.now+=timedelta(minutes=16);d=self.pub.get(ref);self.pub.command(self.body('recover',ref,d['revision']));self.assertEqual(self.pub.get(ref)['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.pub.claim(ref)
 def test_policy_change_or_disabled_worker_prevents_claim(self):
  self.setup_publish();ref=self.create_pub();self.schedule(ref,1);self.now+=timedelta(seconds=2)
  with patch.dict(os.environ,{'COMMERCIAL_PUBLISH_NETWORK_ENABLED':'0'}):
   with self.assertRaises(self.error):self.pub.claim(ref)
  profile={**self.profile,'version':'fixture-2'}
  with patch.dict(os.environ,{'COMMERCIAL_PUBLISH_ACCOUNTS':json.dumps({self.pub.key():{'owned-page-fixture':profile}})}):
   with self.assertRaises(self.error):self.pub.claim(ref)
  self.assertEqual(self.pub.get(ref)['attempts'],0)
 def test_unconfirmed_remote_read_does_not_report_published(self):
  self.setup_publish();ref=self.create_pub();self.schedule(ref,1);self.now+=timedelta(seconds=2);self.pub.dispatch(ref,client_factory=self.mock_client());self.now+=timedelta(seconds=31);self.pub.dispatch(ref,client_factory=self.mock_client('unconfirmed'));self.assertEqual(self.pub.get(ref)['status'],'VERIFY');self.assertIsNone(self.pub.get(ref)['published_at'])
 def test_invalid_asset_or_format_or_visibility_rejected(self):
  self.setup_publish();asset=self.asset()
  for data in [{'format':'UNKNOWN'},{'visibility':'PRIVATE'},{'media_ref':{**asset,'sha256':'0'*64}},{'format':'INSTAGRAM_REEL'},{'account_ref':'https://external.invalid/path'}]:
   with self.assertRaises(self.error):self.pub.command(self.body(**data))
  self.assertEqual(self.pub.list()['jobs'],[])
 def test_history_chain_detects_tampered_event(self):
  self.setup_publish();ref=self.create_pub();store=self.pub.store;original=list(store.events(ref));corrupt=copy.deepcopy(original);corrupt[0]['operation']='forged'
  with patch.object(store,'events',return_value=iter(corrupt)):
   with self.assertRaises(self.error):self.pub.get(ref)
  self.assertTrue(self.pub.history(ref)['history_verified'])
 def adapter_step(self,fmt,stage='SCHEDULED',handler=None,**extra):
  adapter=importlib.import_module(self.module_path+'.publishing_adapters');d={'format':fmt,'claimed_from':stage,'caption':'Laboratorio','title':'Prueba','visibility':'PUBLIC','disclosure':'NONE','asset_snapshot':{'duration_seconds':1},**extra};p={**self.profile,'account_id':'UC'+'x'*22 if fmt=='YOUTUBE_VIDEO' else '123','page_id':'456'};requests=[]
  def send(req):requests.append(req);return handler(req)
  def client(**kwargs):return httpx.Client(transport=httpx.MockTransport(send),**kwargs)
  return adapter.step(d,p,'https://media.example.test/test',raw=b'synthetic-protocol-only-not-a-video',client_factory=client),requests
 def test_instagram_container_completion_is_not_publication(self):
  self.setup_publish()
  def owner(req):return httpx.Response(200,json={'data':[{'id':'456','tasks':['CREATE_CONTENT'],'instagram_business_account':{'id':'123'}}]})
  def send(req):
   if req.url.path.endswith('me/accounts'):return owner(req)
   if req.url.path.endswith('/media'):return httpx.Response(200,json={'id':'777'})
   if req.url.path.endswith('/777'):return httpx.Response(200,json={'id':'777','status_code':'FINISHED'})
   if req.url.path.endswith('media_publish'):return httpx.Response(200,json={'id':'888'})
   return httpx.Response(200,json={'id':'888','owner':{'id':'123'},'media_type':'VIDEO','media_product_type':'REELS','permalink':'https://www.instagram.com/reel/test/'})
  a,_=self.adapter_step('INSTAGRAM_REEL',handler=send);self.assertEqual(a['status'],'WAIT_CONTAINER');self.assertEqual(a['container_id'],'777');b,requests=self.adapter_step('INSTAGRAM_REEL','WAIT_CONTAINER',send,container_id='777');self.assertEqual(b['status'],'READY_TO_PUBLISH');self.assertFalse(any(r.method=='POST' for r in requests));c,_=self.adapter_step('INSTAGRAM_REEL','READY_TO_PUBLISH',send,container_id='777');self.assertEqual(c['status'],'VERIFY');d,_=self.adapter_step('INSTAGRAM_REEL','VERIFY',send,remote_id='888');self.assertEqual(d['status'],'PUBLISHED')
 def test_youtube_upload_requires_processing_and_owned_channel_proof(self):
  self.setup_publish()
  def send(req):
   if req.url.path.endswith('channels'):return httpx.Response(200,json={'items':[{'id':'UC'+'x'*22}]})
   if req.method=='POST':
    self.assertIn(b'multipart',req.headers['content-type'].encode());return httpx.Response(200,json={'id':'abcdefghijk'})
   return httpx.Response(200,json={'items':[{'id':'abcdefghijk','snippet':{'channelId':'UC'+'x'*22},'status':{'uploadStatus':'processed','privacyStatus':'public'},'processingDetails':{'processingStatus':'succeeded'}}]})
  a,_=self.adapter_step('YOUTUBE_VIDEO',handler=send);self.assertEqual(a['status'],'VERIFY');b,requests=self.adapter_step('YOUTUBE_VIDEO','VERIFY',send,remote_id='abcdefghijk');self.assertEqual(b['status'],'PUBLISHED');self.assertFalse(any(r.method=='POST' for r in requests))
 def test_tiktok_init_is_not_completion_and_public_ids_required(self):
  self.setup_publish()
  def send(req):
   if req.url.path.endswith('user/info/'):data={'user':{'open_id':'123'}}
   elif req.url.path.endswith('creator_info/query/'):data={'privacy_level_options':['PUBLIC_TO_EVERYONE'],'max_video_post_duration_sec':120}
   elif req.url.path.endswith('video/init/'):data={'publish_id':'publish-123'}
   else:data={'status':'PUBLISH_COMPLETE','publicaly_available_post_id':['987']}
   return httpx.Response(200,json={'error':{'code':'ok'},'data':data})
  a,_=self.adapter_step('TIKTOK_VIDEO',handler=send);self.assertEqual(a['status'],'VERIFY');b,requests=self.adapter_step('TIKTOK_VIDEO','VERIFY',send,remote_id='publish-123');self.assertEqual(b['status'],'PUBLISHED');self.assertEqual(b['proof']['post_ids'],['987']);self.assertFalse(any(r.url.path.endswith('video/init/') for r in requests))
 def test_wrong_owner_and_generic_remote_200_never_publish(self):
  self.setup_publish()
  for fmt in ('FACEBOOK_PHOTO','INSTAGRAM_REEL','YOUTUBE_VIDEO','TIKTOK_VIDEO'):
   a,requests=self.adapter_step(fmt,handler=lambda req:httpx.Response(200,json={}))
   self.assertEqual(a['status'],'UNCERTAIN');self.assertFalse(any(r.method=='POST' for r in requests))
 def test_provider_redirect_does_not_leak_or_follow_token(self):
  self.setup_publish();a,requests=self.adapter_step('FACEBOOK_PHOTO',handler=lambda req:httpx.Response(302,headers={'Location':'https://external.invalid'}));self.assertEqual(a['status'],'UNCERTAIN');self.assertEqual(len(requests),1);self.assertEqual(requests[0].url.host,'graph.facebook.com')
 def test_post_ack_database_failure_keeps_durable_claim_without_reupload(self):
  self.setup_publish();ref=self.create_pub();self.schedule(ref,1);self.now+=timedelta(seconds=2);factory=self.mock_client()
  with patch.object(self.pub,'finish',side_effect=RuntimeError('synthetic checkpoint write failure')):
   with self.assertRaises(RuntimeError):self.pub.dispatch(ref,client_factory=factory)
  d=self.pub.get(ref);self.assertEqual(d['status'],'DISPATCHING');self.assertEqual(sum(r.method=='POST' for r in self.requests),1)
  with self.assertRaises(self.error):self.pub.dispatch(ref,client_factory=factory)
 def test_different_administrator_cannot_authorize_original_job(self):
  self.setup_publish();ref=self.create_pub();self.pub.actor='different-admin'
  with self.assertRaises(self.error):self.pub.command(self.body('review',ref,1,confirmed_content=True,confirmed_account=True))
 def test_daily_limit_and_poll_delay_prevent_unbounded_dispatch(self):
  self.setup_publish();ref=self.create_pub();self.schedule(ref,1);self.now+=timedelta(seconds=2);self.pub.dispatch(ref,client_factory=self.mock_client())
  with self.assertRaises(self.error):self.pub.claim(ref)
  self.now+=timedelta(seconds=31);self.pub.dispatch(ref,client_factory=self.mock_client('unconfirmed'));self.assertEqual(self.pub.get(ref)['polls'],1)
 def test_owned_video_jobs_use_real_sanitized_library_for_all_video_formats(self):
  self.setup_publish();import subprocess,tempfile
  from pathlib import Path
  with tempfile.TemporaryDirectory(prefix='publication-video-') as directory:
   path=Path(directory)/'test.mp4';subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','color=c=blue:s=720x1280:r=24','-t','3','-an','-c:v','libx264','-pix_fmt','yuv420p','-threads','1',str(path)],check=True,timeout=30);asset=MobileCases.media(self,path.read_bytes(),'video/mp4')
  for fmt,account in [('INSTAGRAM_REEL','123'),('YOUTUBE_VIDEO','UC'+'x'*22),('TIKTOK_VIDEO','123')]:
   profile={**self.profile,'format':fmt,'account_id':account,'page_id':'456'}
   with patch.dict(os.environ,{'COMMERCIAL_PUBLISH_ACCOUNTS':json.dumps({self.pub.key():{'owned-page-fixture':profile}})}):
    ref=self.pub.command(self.body(format=fmt,media_ref=asset))['job_id'];self.schedule(ref,1);self.assertEqual(self.pub.get(ref)['asset_snapshot']['kind'],'VIDEO');self.assertEqual(self.pub.get(ref)['status'],'SCHEDULED')
 def test_invalid_unicode_and_oversized_batch_are_validation_errors(self):
  self.setup_publish()
  with self.assertRaises(self.error):self.pub.command(self.body(caption='\ud800'))
  for limit in [0,51,True,'1']:
   with self.assertRaises(self.error):self.pub.due(limit)
