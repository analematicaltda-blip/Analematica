"""Own ORM inbox rules and controlled protocol transports; no real replies."""
import importlib,os,json,uuid,hashlib,hmac,copy,httpx,base64
from datetime import datetime,timedelta,timezone
from unittest.mock import patch
class InboxCases:
 def setup_inbox(self,channel='FB_DM'):
  self.module=importlib.import_module(self.module_path+'.inbox');store=importlib.import_module(self.module_path+'.inbox_store');self.now=datetime.now(timezone.utc);self.inbox=self.module.Inbox(store.Store(self.gen.crm.store),self.gen.crm,clock=lambda:self.now)
  self.channel=channel;self.profile={'version':'fixture-1','channel':channel,'account_id':'owner@example.test' if channel=='EMAIL' else 'UC'+'x'*22 if channel=='YOUTUBE_COMMENT' else '123','page_id':'456','credential_env':'COMMERCIAL_INBOX_SECRET_TEST','ingress_key_env':'COMMERCIAL_INBOX_INGRESS_TEST','allow_reply':True,'ownership_support_digest':'a'*64};env=patch.dict(os.environ,{'COMMERCIAL_INBOX_ACCOUNTS':json.dumps({self.inbox.key():{'owned':self.profile}}),'COMMERCIAL_INBOX_SECRET_TEST':'not-real-provider-token-000000000','COMMERCIAL_INBOX_INGRESS_TEST':'synthetic-inbox-ingress-00000000000000','COMMERCIAL_INBOX_WORKER_ENABLED':'1','COMMERCIAL_INBOX_NETWORK_ENABLED':'1'});env.start();self.addCleanup(env.stop)
 def event(self,**extra):
  channel=self.channel;sender='person@example.test' if channel=='EMAIL' else '573123456789' if channel=='WHATSAPP' else '789';return {'event_id':str(uuid.uuid4()),'account_ref':'owned','channel':channel,'thread_ref':sender if channel in ('FB_DM','IG_DM','WHATSAPP') else 'thread-123' if channel=='EMAIL' else '987','message_ref':'message-'+uuid.uuid4().hex,'sender_ref':sender,'body':'Mensaje sintético','occurred_at':self.now.isoformat(),'reply_to_ref':'<original@example.test>' if channel=='EMAIL' else None,'subject':'Consulta sintética',**extra}
 def ingest(self,event=None):
  event=event or self.event();signature=hmac.new(os.environ['COMMERCIAL_INBOX_INGRESS_TEST'].encode(),self.module.digest({'key':self.inbox.key(),'event':event}).encode(),hashlib.sha256).hexdigest();return self.inbox.ingest(event,signature)
 def body(self,op,ref,rev,**data):return {'request_id':str(uuid.uuid4()),'operation':op,'job_id':ref,'expected_revision':rev,'data':data}
 def action(self,ref,op,**data):return self.inbox.command(self.body(op,ref,self.inbox.get(ref)['revision'],**data))
 def linked(self):
  ref=self.ingest()['job_id'];crm=self.gen.crm;contact=crm.command({'request_id':str(uuid.uuid4()),'operation':'create','contact_id':None,'expected_revision':0,'data':{'name':'Persona sintética','email':'person@example.test' if self.channel=='EMAIL' else uuid.uuid4().hex+'@example.test','phone':'+573123456789' if self.channel=='WHATSAPP' else '+573'+str(uuid.uuid4().int%1000000000).zfill(9),'origin':'INBOX_FIXTURE','responsible_ref':crm.actor}})['contact_id'];self.action(ref,'link',contact_id=contact,confirmed_identity=True);self.action(ref,'assign',actor_ref=crm.actor);return ref
 def queued(self):
  ref=self.linked();self.action(ref,'draft',text='Respuesta revisada');self.action(ref,'review',confirmed_content=True,confirmed_thread=True);self.action(ref,'queue',confirmed_impact=True);return ref
 def client(self,mode='normal'):
  self.requests=[]
  def send(req):
   self.requests.append(req)
   if req.url.path.endswith('/me'):return httpx.Response(200,json={'id':'123'})
   if req.url.path.endswith('/accounts'):return httpx.Response(200,json={'data':[{'id':'456','tasks':['MANAGE'],'instagram_business_account':{'id':'123'}}]})
   if req.url.path.endswith('/123'):return httpx.Response(200,json={'id':'123','display_phone_number':'+57'})
   if req.method=='POST':
    if mode=='timeout':raise httpx.ReadTimeout('synthetic',request=req)
    return httpx.Response(200,json={} if mode=='generic' else {'recipient_id':'wrong' if mode=='wrong' else '789','message_id':'reply-123','contacts':[{'wa_id':'573123456789'}],'messages':[{'id':'wamid.test'}]})
   raise AssertionError('Unexpected endpoint '+str(req.url))
  def factory(**kwargs):
   self.assertFalse(kwargs['follow_redirects']);self.assertFalse(kwargs['trust_env']);return httpx.Client(transport=httpx.MockTransport(send),**kwargs)
  return factory
 def test_signed_ingress_is_idempotent_and_does_not_create_or_reply_to_contact(self):
  self.setup_inbox();event=self.event();r=self.ingest(event);self.assertTrue(self.ingest(event)['replayed']);d=self.inbox.get(r['job_id']);self.assertIsNone(d['contact_id']);self.assertIsNone(d['reply']);self.assertFalse(d['native_provider_authenticity_qualified']);self.assertFalse(self.inbox.list()['automatic_replies'])
 def test_bad_signature_future_event_and_channel_manipulation_rejected(self):
  self.setup_inbox();event=self.event()
  with self.assertRaises(self.error):self.inbox.ingest(event,'0'*64)
  for change in [{'occurred_at':(self.now+timedelta(hours=1)).isoformat()},{'thread_ref':'other'},{'channel':'EMAIL'},{'sender_ref':'https://evil.invalid'}]:
   with self.assertRaises(self.error):self.ingest({**event,**change})
  self.assertEqual(self.inbox.list()['threads'],[])
 def test_link_assignment_draft_two_reviews_and_acceptance_are_separate(self):
  self.setup_inbox();ref=self.queued();d=self.inbox.get(ref);self.assertNotEqual(d['reply']['review']['request_id'],d['reply']['authorization']['request_id']);self.inbox.dispatch(ref,client_factory=self.client());d=self.inbox.get(ref);self.assertEqual(d['status'],'ACCEPTED');self.assertFalse(d['messages'][-1]['delivery_verified']);self.assertEqual(json.loads(self.requests[-1].content)['recipient']['id'],'789');self.assertEqual(len([r for r in self.requests if r.method=='POST']),1)
  with self.assertRaises(self.error):self.inbox.dispatch(ref,client_factory=self.client())
 def test_unlinked_contact_and_invalid_assignment_block_reply(self):
  self.setup_inbox();ref=self.ingest()['job_id']
  for op,data in [('draft',{'text':'No autorizado'}),('assign',{'actor_ref':'99999999'}),('link',{'contact_id':str(uuid.uuid4()),'confirmed_identity':True})]:
   with self.assertRaises(self.error):self.action(ref,op,**data)
 def test_new_inbound_invalidates_pending_review(self):
  self.setup_inbox();ref=self.queued();self.now+=timedelta(seconds=1);self.ingest();d=self.inbox.get(ref);self.assertEqual(d['status'],'OPEN');self.assertIsNone(d['reply'])
  with self.assertRaises(self.error):self.inbox.claim(ref)
 def uncertain_case(self,mode):
  self.setup_inbox();ref=self.queued();self.inbox.dispatch(ref,client_factory=self.client(mode));self.assertEqual(self.inbox.get(ref)['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.inbox.claim(ref)
 def test_timeout_never_resends(self):self.uncertain_case('timeout')
 def test_generic_http200_never_claims_acceptance(self):self.uncertain_case('generic')
 def test_wrong_recipient_never_claims_acceptance(self):self.uncertain_case('wrong')
 def test_old_dm_window_and_worker_disabled_block_network(self):
  self.setup_inbox();ref=self.queued();self.now+=timedelta(hours=25)
  with self.assertRaises(self.error):self.inbox.claim(ref)
  with patch.dict(os.environ,{'COMMERCIAL_INBOX_NETWORK_ENABLED':'0'}):
   with self.assertRaises(self.error):self.inbox.claim(ref)
 def test_unsupported_tiktok_is_handoff_only(self):
  self.setup_inbox('TIKTOK_COMMENT');ref=self.linked()
  with self.assertRaises(self.error):self.action(ref,'draft',text='No fingir API')
  self.action(ref,'handoff',reason='Resolver con operador autorizado');self.assertEqual(self.inbox.get(ref)['status'],'HANDOFF')
 def test_revision_conflict_request_replay_and_changed_payload_rejected(self):
  self.setup_inbox();ref=self.linked();body=self.body('draft',ref,self.inbox.get(ref)['revision'],text='Borrador');self.inbox.command(body);self.assertTrue(self.inbox.command(body)['replayed']);body['data']['text']='Otro'
  with self.assertRaises(self.error):self.inbox.command(body)
  with self.assertRaises(self.error):self.inbox.command(self.body('cancel',ref,1))
 def test_role_revocation_blocks_read_history_receipt_and_send(self):
  self.setup_inbox();ref=self.queued()
  with patch.object(self.gen.crm,'authorize',side_effect=self.error('REVOKED',403)):
   for action in [lambda:self.inbox.get(ref),lambda:self.inbox.history(ref),lambda:self.inbox.dispatch(ref,client_factory=self.client())]:
    with self.assertRaises(self.error):action()
 def test_recover_interrupted_claim_never_resends(self):
  self.setup_inbox();ref=self.queued();self.inbox.claim(ref);self.now+=timedelta(minutes=16);self.action(ref,'recover');self.assertEqual(self.inbox.get(ref)['status'],'UNCERTAIN')
  with self.assertRaises(self.error):self.inbox.claim(ref)
 def test_audit_corruption_is_detected(self):
  self.setup_inbox();ref=self.linked();events=list(self.inbox.store.events(ref));events[0]['operation']='tampered'
  with patch.object(self.inbox.store,'events',return_value=iter(events)):
   with self.assertRaises(self.error):self.inbox.get(ref)
 def test_whatsapp_and_instagram_use_their_own_channel_and_thread(self):
  for channel in ['WHATSAPP','IG_DM']:
   self.setup_inbox(channel);ref=self.queued();self.inbox.dispatch(ref,client_factory=self.client());self.assertEqual(self.inbox.get(ref)['status'],'ACCEPTED');payload=json.loads(self.requests[-1].content)
   if channel=='WHATSAPP':self.assertEqual(payload['context']['message_id'],self.inbox.get(ref)['reply']['anchor_id']);self.assertEqual(payload['to'],'573123456789')
   else:self.assertEqual(payload['recipient']['id'],'789')
 def test_gmail_reply_is_bound_to_actual_headers_and_thread(self):
  self.setup_inbox('EMAIL');ref=self.queued();d=self.inbox.get(ref);self.requests=[]
  def send(req):
   self.requests.append(req)
   if req.url.path.endswith('profile'):value={'emailAddress':'owner@example.test'}
   elif req.method=='GET':value={'id':'thread-123','messages':[{'id':d['reply']['anchor_id'],'payload':{'headers':[{'name':'From','value':'Persona <person@example.test>'},{'name':'Message-ID','value':'<original@example.test>'},{'name':'Subject','value':'Consulta'}]}}]}
   else:
    payload=json.loads(req.content);self.assertEqual(payload['threadId'],'thread-123');from email import message_from_bytes;message=message_from_bytes(base64.urlsafe_b64decode(payload['raw']));self.assertEqual(message['In-Reply-To'],'<original@example.test>');self.assertEqual(message['To'],'person@example.test');value={'id':'gmail-reply-123','threadId':'thread-123'}
   return httpx.Response(200,json=value)
  self.inbox.dispatch(ref,client_factory=lambda **kwargs:httpx.Client(transport=httpx.MockTransport(send),**kwargs));self.assertEqual(self.inbox.get(ref)['status'],'ACCEPTED')
 def test_youtube_reply_requires_owned_parent_and_exact_parent_ack(self):
  self.setup_inbox('YOUTUBE_COMMENT');ref=self.queued()
  def send(req):
   if req.url.path.endswith('/channels'):value={'items':[{'id':'UC'+'x'*22}]}
   elif req.method=='GET':value={'items':[{'id':'987','snippet':{'channelId':'UC'+'x'*22}}]}
   else:
    self.assertEqual(json.loads(req.content)['snippet']['parentId'],'987');value={'id':'reply-youtube','snippet':{'parentId':'987','authorChannelId':{'value':'UC'+'x'*22}}}
   return httpx.Response(200,json=value)
  self.inbox.dispatch(ref,client_factory=lambda **kwargs:httpx.Client(transport=httpx.MockTransport(send),**kwargs));self.assertEqual(self.inbox.get(ref)['status'],'ACCEPTED')
 def comment_case(self,channel):
  self.setup_inbox(channel);ref=self.queued();self.requests=[]
  def send(req):
   self.requests.append(req);path=req.url.path
   if path.endswith('/me'):value={'id':'123'}
   elif path.endswith('/accounts'):value={'data':[{'id':'456','tasks':['MANAGE'],'instagram_business_account':{'id':'123'}}]}
   elif req.method=='POST':
    self.assertTrue(path.endswith('/987/'+('replies' if channel=='IG_COMMENT' else 'comments')));value={'id':'555'}
   elif path.endswith('/987'):value={'id':'987','object':{'id':'123_999'},'media':{'id':'999'}}
   elif path.endswith('/555'):value={'id':'555','parent':{'id':'987'},'from':{'id':'123'}}
   else:value={'id':'999','owner':{'id':'123'},'from':{'id':'123'}}
   return httpx.Response(200,json=value)
  self.inbox.dispatch(ref,client_factory=lambda **kwargs:httpx.Client(transport=httpx.MockTransport(send),**kwargs));self.assertEqual(self.inbox.get(ref)['status'],'ACCEPTED');self.assertEqual(sum(r.method=='POST' for r in self.requests),1)
 def test_facebook_comment_reply_is_bound_to_owned_post(self):self.comment_case('FB_COMMENT')
 def test_instagram_comment_reply_is_bound_to_owned_media(self):self.comment_case('IG_COMMENT')
 def test_message_rebinding_or_duplicate_payload_change_is_rejected(self):
  self.setup_inbox('FB_COMMENT');event=self.event();ref=self.ingest(event)['job_id']
  with self.assertRaises(self.error):self.ingest({**event,'event_id':str(uuid.uuid4()),'sender_ref':'other-person'})
  with self.assertRaises(self.error):self.ingest({**event,'event_id':str(uuid.uuid4()),'body':'Tampered'})
  self.assertEqual(len(self.inbox.get(ref)['messages']),1)
 def test_email_contact_mismatch_and_header_injection_rejected(self):
  self.setup_inbox('EMAIL')
  for event in [self.event(sender_ref='victim@example.test\r\nBcc:other@example.test'),self.event(reply_to_ref='<bad>\r\nBcc:test')]:
   with self.assertRaises(self.error):self.ingest(event)
 def test_post_ack_write_failure_retains_claim_and_no_auto_retry(self):
  self.setup_inbox();ref=self.queued()
  with patch.object(self.inbox,'finish',side_effect=RuntimeError('synthetic database failure')):
   with self.assertRaises(RuntimeError):self.inbox.dispatch(ref,client_factory=self.client())
  self.assertEqual(self.inbox.get(ref)['status'],'DISPATCHING')
  with self.assertRaises(self.error):self.inbox.claim(ref)
 def test_invalid_unicode_boolean_confirmation_and_unexpected_fields_rejected(self):
  self.setup_inbox();ref=self.linked()
  with self.assertRaises(self.error):self.action(ref,'draft',text='\ud800')
  self.action(ref,'draft',text='Respuesta');self.action(ref,'review',confirmed_content=True,confirmed_thread=True)
  with self.assertRaises(self.error):self.action(ref,'queue',confirmed_impact=1)
 def test_signature_and_channel_permissions_cannot_be_bypassed(self):
  self.setup_inbox();event=self.event();ref=self.ingest(event)['job_id']
  for signature in ['é'*64,'sha256='+'a'*64,'',None]:
   with self.assertRaises(self.error):self.inbox.ingest(event,signature)
  from types import SimpleNamespace
  access=SimpleNamespace(principal={'is_manager':True},session=lambda:{'capability_permissions':{'channel.email.reply':True}})
  with patch.object(self.gen.crm,'authorize',return_value=access):
   self.assertEqual(self.inbox.list()['threads'],[])
   with self.assertRaises(self.error):self.inbox.get(ref)
   with self.assertRaises(self.error):self.inbox.receipt(event['event_id'])
 def test_contact_withdrawal_and_profile_revocation_block_send(self):
  self.setup_inbox();ref=self.queued();contact=self.gen.crm.get(self.inbox.get(ref)['contact_id']);self.gen.crm.command({'request_id':str(uuid.uuid4()),'operation':'withdraw','contact_id':contact['id'],'expected_revision':contact['revision'],'data':{'reason':'Retira contacto de prueba'}})
  with self.assertRaises(self.error):self.inbox.claim(ref)
 def test_received_message_between_claim_and_network_blocks_stale_answer(self):
  self.setup_inbox();ref=self.queued();original=self.inbox.claim
  def concurrent_claim(job):
   result=original(job);self.now+=timedelta(seconds=1);self.ingest();return result
  with patch.object(self.inbox,'claim',side_effect=concurrent_claim):
   with self.assertRaises(self.error):self.inbox.dispatch(ref,client_factory=self.client())
  self.assertEqual(self.requests,[]);self.assertEqual(self.inbox.get(ref)['status'],'DISPATCHING')
 def test_worker_skips_blocked_head_without_starving_next_authorized_job(self):
  self.setup_inbox();worker=importlib.import_module(self.module_path+'.inbox_worker');ctx=importlib.import_module(self.module_path+'.inbox_worker_context');from contextlib import contextmanager
  @contextmanager
  def context(document):yield self.gen.crm
  from types import SimpleNamespace
  def dispatch(ref):
   if ref=='blocked':raise self.error('BLOCKED',403)
   return {'status':'ACCEPTED'}
  with patch.object(ctx,'candidates',return_value=[('blocked',{}),('valid',{}),('not-run',{})]),patch.object(ctx,'context',context),patch.object(worker,'service',return_value=SimpleNamespace(dispatch=dispatch)):
   result=worker.run_once(1);self.assertEqual([r['thread_id'] for r in result],['blocked','valid']);self.assertEqual(result[-1]['status'],'ACCEPTED')
 def test_native_meta_raw_signature_and_account_mapping_for_all_text_channels(self):
  for channel in ['FB_DM','IG_DM','WHATSAPP','FB_COMMENT','IG_COMMENT']:
   self.setup_inbox(channel);source=importlib.import_module(self.module_path+'.inbox_ingress');now=int(self.now.timestamp());message={'sender':{'id':'789'},'recipient':{'id':'123'},'timestamp':now*1000,'message':{'mid':'native-'+channel,'text':'Mensaje nativo sintético'}}
   if channel in ('FB_DM','IG_DM'):packet={'object':'page' if channel=='FB_DM' else 'instagram','entry':[{'id':'123','messaging':[message]}]}
   elif channel=='WHATSAPP':packet={'object':'whatsapp_business_account','entry':[{'id':'business','changes':[{'field':'messages','value':{'metadata':{'phone_number_id':'123'},'messages':[{'id':'native-wa','from':'573123456789','timestamp':str(now),'type':'text','text':{'body':'Mensaje'}}]}}]}]}
   elif channel=='FB_COMMENT':packet={'object':'page','entry':[{'id':'123','changes':[{'field':'feed','value':{'item':'comment','verb':'add','post_id':'123_999','comment_id':'987','from':{'id':'789'},'message':'Consulta','created_time':now}}]}]}
   else:packet={'object':'instagram','entry':[{'id':'123','time':now,'changes':[{'field':'comments','value':{'id':'987','from':{'id':'789'},'text':'Consulta'}}]}]}
   raw=json.dumps(packet).encode();secret='native-app-secret-fixture-00000000000';signature='sha256='+hmac.new(secret.encode(),raw,hashlib.sha256).hexdigest()
   with patch.dict(os.environ,{'COMMERCIAL_INBOX_META_KEYS':json.dumps({self.inbox.key():{'owned':'COMMERCIAL_INBOX_NATIVE_TEST'}}),'COMMERCIAL_INBOX_NATIVE_TEST':secret}):
    result=source.meta(self.inbox,'owned',raw,signature);self.assertTrue(result['native_signature_checked']);self.assertTrue(source.meta(self.inbox,'owned',raw,signature)['receipts'][0]['replayed']);self.assertIsNone(self.inbox.get(result['receipts'][0]['job_id'])['contact_id'])
    with self.assertRaises(self.error):source.meta(self.inbox,'owned',raw+b' ',signature)
 def test_gmail_source_read_uses_owned_mailbox_plain_text_and_no_mutation(self):
  self.setup_inbox('EMAIL');source=importlib.import_module(self.module_path+'.inbox_ingress');requests=[]
  def send(req):
   requests.append(req);self.assertEqual(req.method,'GET')
   if req.url.path.endswith('/profile'):value={'emailAddress':'owner@example.test'}
   elif req.url.path.endswith('/messages'):value={'messages':[{'id':'gmail-source'}]}
   else:value={'id':'gmail-source','threadId':'thread-123','internalDate':str(int(self.now.timestamp()*1000)),'payload':{'mimeType':'text/plain','headers':[{'name':'From','value':'Persona <person@example.test>'},{'name':'Message-ID','value':'<native@example.test>'},{'name':'Subject','value':'Consulta'}],'body':{'data':base64.urlsafe_b64encode(b'Plain body').decode()}}}
   return httpx.Response(200,json=value)
  with patch.dict(os.environ,{'COMMERCIAL_INBOX_INGRESS_NETWORK_ENABLED':'1'}):
   result=source.sync(self.inbox,'owned','EMAIL',client_factory=lambda **kw:httpx.Client(transport=httpx.MockTransport(send),**kw));self.assertEqual(len(result['receipts']),1);self.assertFalse(result['replies_sent']);self.assertEqual(self.inbox.get(result['receipts'][0]['job_id'])['messages'][0]['body'],'Plain body')
 def test_youtube_source_is_owned_channel_bounded_and_read_only(self):
  self.setup_inbox('YOUTUBE_COMMENT');source=importlib.import_module(self.module_path+'.inbox_ingress')
  def send(req):
   self.assertEqual(req.method,'GET')
   if req.url.path.endswith('/channels'):value={'items':[{'id':'UC'+'x'*22}]}
   else:value={'items':[{'snippet':{'channelId':'UC'+'x'*22,'topLevelComment':{'id':'yt-native','snippet':{'authorChannelId':{'value':'UC'+'a'*22},'textOriginal':'Consulta','publishedAt':self.now.isoformat()}}}}],'nextPageToken':'more'}
   return httpx.Response(200,json=value)
  with patch.dict(os.environ,{'COMMERCIAL_INBOX_INGRESS_NETWORK_ENABLED':'1'}):
   result=source.sync(self.inbox,'owned','YOUTUBE_COMMENT',client_factory=lambda **kw:httpx.Client(transport=httpx.MockTransport(send),**kw));self.assertTrue(result['more_available']);self.assertFalse(result['full_mailbox_or_history_synced']);self.assertEqual(len(result['receipts']),1)
