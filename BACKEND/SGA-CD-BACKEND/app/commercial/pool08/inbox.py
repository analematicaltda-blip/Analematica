"""Private owned omnichannel inbox. Normalized ingress is not a native webhook.

Its scoped HMAC authenticates the trusted connector, not the identity of a sender.
Unlinked events never trigger an outbound response. No model auto-sends messages.
"""
import copy,os,json,re,hashlib,hmac,uuid,secrets
from datetime import datetime,timedelta,timezone
from .crm import CRMError,text,digest as base_digest,moment
from .opportunities import uuid_ref
from .email_campaigns import contact_ref
from .contract import SYSTEM
MAX_RECORDS=500
CHANNELS={'FB_DM':'channel.private_message.reply','IG_DM':'channel.private_message.reply','WHATSAPP':'channel.private_message.reply','FB_COMMENT':'channel.public_comment.reply','IG_COMMENT':'channel.public_comment.reply','YOUTUBE_COMMENT':'channel.public_comment.reply','EMAIL':'channel.email.reply','TIKTOK_DM':'channel.private_message.reply','TIKTOK_COMMENT':'channel.public_comment.reply'}
UNSUPPORTED={'TIKTOK_DM','TIKTOK_COMMENT'}
def digest(value):
 try:return base_digest(value)
 except UnicodeError:raise CRMError('INBOX_INVALID_TEXT') from None
def remote_ref(value):
 if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9_@.+<>=:-]{1,200}',value):raise CRMError('INBOX_INVALID_REMOTE_REFERENCE')
 return value
class Inbox:
 def __init__(self,store,crm,clock=None):self.store,self.crm=store,crm;self.actor=crm.actor;self.clock=clock or (lambda:datetime.now(timezone.utc))
 def authority(self,channel=None):
  access=self.crm.authorize();caps=access.session()['capability_permissions']
  if not access.principal['is_manager'] or not (caps.get(CHANNELS[channel]) if channel else any(caps.get(v) for v in CHANNELS.values())):raise CRMError('INBOX_PERMISSION_REQUIRED',403)
 def key(self):return SYSTEM+':'+self.store.scope+':'+(getattr(self.store,'provider',None) or '-')
 def profile(self,account,channel):
  try:
   p=json.loads(os.environ.get('COMMERCIAL_INBOX_ACCOUNTS','{}'))[self.key()][account]
   required={'version','channel','account_id','page_id','credential_env','ingress_key_env','allow_reply','ownership_support_digest'}
   if not isinstance(p,dict) or set(p)!=required or p['channel']!=channel or type(p['allow_reply'])!=bool:raise ValueError()
   text(p['version'],80);remote_ref(p['account_id'])
   if not re.fullmatch('COMMERCIAL_INBOX_SECRET_[A-Z0-9_]{1,60}',str(p['credential_env'])) or not re.fullmatch('COMMERCIAL_INBOX_INGRESS_[A-Z0-9_]{1,60}',str(p['ingress_key_env'])) or not re.fullmatch('[a-f0-9]{64}',str(p['ownership_support_digest'])):raise ValueError()
   if channel=='IG_DM':remote_ref(p['page_id'])
   return copy.deepcopy(p)
  except (ValueError,KeyError,TypeError,AttributeError):raise CRMError('INBOX_ACCOUNT_PROFILE_REQUIRED',503) from None
 def raw(self,ref):
  uuid_ref(ref);d=self.store.get(ref)
  if not d:raise CRMError('INBOX_RECORD_NOT_FOUND',404)
  previous='0'*64;events=list(self.store.events(ref))
  for e in events:
   if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('INBOX_HISTORY_REVIEW_REQUIRED',503)
   previous=e['event_digest']
  if not events or len(events)!=d['revision'] or previous!=d['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('INBOX_INTEGRITY_REVIEW_REQUIRED',503)
  return d
 def get(self,ref):self.authority();d=self.raw(ref);self.authority();return d
 def records(self):
  rows=list(self.store.all_jobs())
  if len(rows)>MAX_RECORDS:raise CRMError('INBOX_RECORD_LIMIT',409)
  return [self.raw(r['id']) for r in rows]
 def emit(self,d,rid,op,signature,expected):
  d['revision']=expected+1;d['updated_at']=self.clock().isoformat();receipt={'request_id':rid,'job_id':d['id'],'status':d['status'],'revision':d['revision'],'network_call_by_command':op.startswith('worker_')}
  e={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':d['id'],'operation':op,'fingerprint':signature,'previous_event_digest':d.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in d.items() if k!='last_event_digest'}),'receipt':receipt,'created_at':self.clock().isoformat()};e['event_digest']=digest(e);d['last_event_digest']=e['event_digest'];self.store.save(d,expected);self.store.append(e);return receipt
 def history(self,ref):
  self.get(ref);return {'events':list(self.store.events(ref)),'history_verified':True}
 def receipt(self,rid):
  self.authority();uuid_ref(rid);e=self.store.event(rid)
  if not e or e.get('scope')!=self.store.scope or e.get('provider_ref')!=getattr(self.store,'provider',None) or e.get('actor')!=self.actor:raise CRMError('INBOX_RECEIPT_NOT_FOUND',404)
  self.get(e['item_id']);return e['receipt']|{'previous_receipt_only':True}
 def list(self):
  self.authority();return {'threads':[{k:d[k] for k in ('id','title','channel','account_ref','contact_id','assigned_to','status','revision','updated_at')} for d in self.records() if self.allowed(d['channel'])],'automatic_replies':False,'native_provider_authenticity_qualified':False,'unsupported_reply_channels':sorted(UNSUPPORTED)}
 def allowed(self,channel):
  try:self.authority(channel);return True
  except CRMError:return False
 def get(self,ref):
  self.authority();d=self.raw(ref);self.authority(d['channel']);return d
 def ingest(self,event,signature):
  self.authority()
  fields={'event_id','account_ref','channel','thread_ref','message_ref','sender_ref','body','occurred_at','reply_to_ref','subject'}
  if not isinstance(event,dict) or set(event)!=fields or not isinstance(event['channel'],str) or event['channel'] not in CHANNELS:raise CRMError('INBOX_INVALID_EVENT')
  channel=event['channel'];self.authority(channel);rid=uuid_ref(event['event_id']);account=text(event['account_ref'],100);p=self.profile(account,channel)
  for k in ('thread_ref','message_ref','sender_ref'):remote_ref(event[k])
  if channel in ('FB_DM','IG_DM','WHATSAPP') and event['thread_ref']!=event['sender_ref']:raise CRMError('INBOX_DM_THREAD_MUST_MATCH_SENDER')
  if channel=='EMAIL':
   if not re.fullmatch(r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,63}',event['sender_ref']) or not re.fullmatch(r'<[A-Za-z0-9._+=@-]{1,180}>',event['reply_to_ref']):raise CRMError('INBOX_EMAIL_HEADERS_REQUIRED')
  elif event['reply_to_ref'] is not None:raise CRMError('INBOX_INVALID_REPLY_HEADER')
  text(event['body'],4000);text(event['subject'],200,optional=True)
  when=moment(event['occurred_at'])
  if when>self.clock()+timedelta(minutes=5) or when<self.clock()-timedelta(days=30):raise CRMError('INBOX_EVENT_TIME_RANGE')
  envelope={'key':self.key(),'event':event};fingerprint=digest(envelope);secret=os.environ.get(p['ingress_key_env'],'')
  if not isinstance(secret,str) or not 32<=len(secret)<=256:raise CRMError('INBOX_INGRESS_KEY_REQUIRED',503)
  expected=hmac.new(secret.encode(),fingerprint.encode(),hashlib.sha256).hexdigest()
  if not isinstance(signature,str) or not re.fullmatch('[a-f0-9]{64}',signature) or not hmac.compare_digest(signature,expected):raise CRMError('INBOX_CONNECTOR_SIGNATURE_REQUIRED',403)
  ref=str(uuid.uuid5(uuid.NAMESPACE_URL,self.key()+':'+channel+':'+account+':'+event['thread_ref']+':'+event['sender_ref']))
  with self.store.transaction():
   self.store.lock();self.authority(channel);prior=self.store.event(rid)
   if prior:
    if prior.get('fingerprint')!=fingerprint or prior.get('scope')!=self.store.scope or prior.get('provider_ref')!=getattr(self.store,'provider',None):raise CRMError('INBOX_EVENT_CONFLICT',409)
    self.get(prior['item_id']);return prior['receipt']|{'replayed':True}
   if any(j['id']!=ref and j['channel']==channel and j['account_ref']==account and any(m['direction']=='IN' and m['remote_id']==event['message_ref'] for m in j['messages']) for j in self.records()):raise CRMError('INBOX_MESSAGE_THREAD_CONFLICT',409)
   previous=self.store.get(ref)
   if previous:
    d=copy.deepcopy(self.get(ref))
    if d['sender_ref']!=event['sender_ref'] and channel not in ('EMAIL','FB_COMMENT','IG_COMMENT','YOUTUBE_COMMENT','TIKTOK_COMMENT'):raise CRMError('INBOX_SENDER_BINDING_CONFLICT',409)
    # Never attach another participant to an existing contact identity silently.
    if d['sender_ref']!=event['sender_ref']:raise CRMError('INBOX_PARTICIPANT_REVIEW_REQUIRED',409)
    if any(m['direction']=='IN' and m['remote_id']==event['message_ref'] for m in d['messages']):
     original=next(m for m in d['messages'] if m['direction']=='IN' and m['remote_id']==event['message_ref'])
     if original['event_digest']!=digest({k:v for k,v in event.items() if k!='event_id'}):raise CRMError('INBOX_MESSAGE_CONFLICT',409)
     return self.emit(d,rid,'duplicate_message',fingerprint,d['revision'])
    if len(d['messages'])>=(99 if d['status']=='DISPATCHING' else 100):raise CRMError('INBOX_THREAD_MESSAGE_LIMIT',409)
    if d['status'] in ('DRAFT','REVIEWED','QUEUED','CLOSED','HANDOFF'):
     d['reply']=None;d['status']='OPEN';d['error_code']='NEW_MESSAGE_REVIEW_REQUIRED'
   else:
    if len(self.records())>=200:raise CRMError('INBOX_THREAD_LIMIT',409)
    d={'id':ref,'code':ref,'kind':'THREAD','title':text(event['subject'],200,optional=True) or channel+' · '+account,'channel':channel,'account_ref':account,'sender_ref':event['sender_ref'],'thread_ref':event['thread_ref'],'contact_id':None,'assigned_to':None,'status':'OPEN','creator_ref':self.actor,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'revision':0,'created_at':self.clock().isoformat(),'reply':None,'messages':[],'native_provider_authenticity_qualified':False,'error_code':None}
   d['messages'].append({'direction':'IN','remote_id':event['message_ref'],'body':event['body'],'occurred_at':when.isoformat(),'reply_to_ref':event['reply_to_ref'],'event_digest':digest({k:v for k,v in event.items() if k!='event_id'})})
   latest=max((m for m in d['messages'] if m['direction']=='IN'),key=lambda m:(m['occurred_at'],m['remote_id']));d['last_inbound_id']=latest['remote_id'];d['last_inbound_at']=latest['occurred_at']
   return self.emit(d,rid,'connector_ingress',fingerprint,d['revision'])
 def eligible(self,d):
  if not d['contact_id'] or not d['assigned_to'] or not self.crm.member(d['assigned_to']):raise CRMError('INBOX_LINK_AND_ASSIGNMENT_REQUIRED',409)
  c=self.crm.get(d['contact_id'])
  if c['status'] in ('WITHDRAWN','ARCHIVED','DUPLICATE'):raise CRMError('INBOX_CONTACT_NOT_ACTIVE',409)
  if d['channel']=='EMAIL' and c.get('email','').lower()!=d['sender_ref'].lower():raise CRMError('INBOX_EMAIL_CONTACT_MISMATCH',409)
  if d['channel']=='WHATSAPP' and str(c.get('phone','')).lstrip('+')!=d['sender_ref']:raise CRMError('INBOX_PHONE_CONTACT_MISMATCH',409)
  if d['channel'] in ('FB_DM','IG_DM','WHATSAPP') and moment(d['last_inbound_at'])+timedelta(hours=24)<=self.clock():raise CRMError('INBOX_RESPONSE_WINDOW_EXPIRED',409)
  if d['channel'] in UNSUPPORTED:raise CRMError('INBOX_PROVIDER_REPLY_UNSUPPORTED',409)
 def command(self,body):
  self.authority()
  if not isinstance(body,dict) or set(body)!={'request_id','operation','job_id','expected_revision','data'} or type(body['expected_revision'])!=int or not 1<=body['expected_revision']<1000 or not isinstance(body['data'],dict):raise CRMError('INBOX_INVALID_COMMAND')
  rid=uuid_ref(body['request_id']);ref=uuid_ref(body['job_id']);op=body['operation'];data=body['data'];fingerprint=digest({'key':self.key(),'actor':self.actor,'body':body})
  with self.store.transaction():
   self.store.lock();d=copy.deepcopy(self.get(ref));prior=self.store.event(rid)
   if prior:
    self.receipt(rid)
    if prior['fingerprint']!=fingerprint:raise CRMError('INBOX_REQUEST_CONFLICT',409)
    return prior['receipt']|{'replayed':True}
   if d['revision']!=body['expected_revision']:raise CRMError('INBOX_REVISION_CONFLICT',409)
   if op=='link' and d['status'] not in ('DISPATCHING','QUEUED') and set(data)=={'contact_id','confirmed_identity'} and data['confirmed_identity'] is True:
    self.crm.get(contact_ref(data['contact_id']));d['contact_id']=data['contact_id'];d['reply']=None;d['status']='OPEN'
   elif op=='assign' and d['status'] not in ('DISPATCHING','QUEUED') and set(data)=={'actor_ref'} and isinstance(data['actor_ref'],str) and self.crm.member(data['actor_ref']):d['assigned_to']=data['actor_ref'];d['reply']=None;d['status']='OPEN'
   elif op=='draft' and d['status'] in ('OPEN','DRAFT','ACCEPTED','HANDOFF') and set(data)=={'text'}:
    self.eligible(d);p=self.profile(d['account_ref'],d['channel']);d['creator_ref']=self.actor;d['reply']={'text':text(data['text'],2000),'creator_ref':self.actor,'anchor_id':d['last_inbound_id'],'profile_digest':digest(p),'review':None,'authorization':None,'remote_id':None};d['status']='DRAFT'
   elif op=='review' and d['status']=='DRAFT' and data=={'confirmed_content':True,'confirmed_thread':True} and all(type(v)==bool for v in data.values()):
    self.eligible(d)
    if d['reply']['creator_ref']!=self.actor:raise CRMError('INBOX_SAME_ADMIN_REQUIRED',403)
    d['reply']['review']={'actor':self.actor,'request_id':rid};d['status']='REVIEWED'
   elif op=='queue' and d['status']=='REVIEWED' and data=={'confirmed_impact':True} and type(data['confirmed_impact'])==bool:
    self.eligible(d)
    if d['reply']['creator_ref']!=self.actor or digest(self.profile(d['account_ref'],d['channel']))!=d['reply']['profile_digest']:raise CRMError('INBOX_REVIEW_CHANGED',409)
    d['reply']['authorization']={'actor':self.actor,'request_id':rid};d['status']='QUEUED'
   elif op=='cancel' and not data and d['status'] in ('DRAFT','REVIEWED','QUEUED'):d['reply']=None;d['status']='OPEN'
   elif op=='handoff' and d['status'] not in ('DISPATCHING','QUEUED') and set(data)=={'reason'}:d['handoff_reason']=text(data['reason'],500);d['status']='HANDOFF';d['reply']=None
   elif op=='close' and not data and d['status'] not in ('DISPATCHING','QUEUED'):d['status']='CLOSED';d['reply']=None
   elif op=='recover' and not data and d['status']=='DISPATCHING' and moment(d['claimed_at'])+timedelta(minutes=15)<=self.clock():d['status']='UNCERTAIN';d['claim_hash']=None;d['error_code']='NO_AUTOMATIC_RESEND';d['messages'].append({'direction':'OUT','body':d['reply']['text'],'remote_id':None,'anchor_id':d['reply']['anchor_id'],'status':'UNCERTAIN','occurred_at':self.clock().isoformat(),'delivery_verified':False})
   else:raise CRMError('INBOX_STATE_REQUIRED',409)
   return self.emit(d,rid,op,fingerprint,body['expected_revision'])
 def claim(self,ref):
  if os.environ.get('COMMERCIAL_INBOX_WORKER_ENABLED')!='1' or os.environ.get('COMMERCIAL_INBOX_NETWORK_ENABLED')!='1':raise CRMError('INBOX_WORKER_DISABLED',503)
  with self.store.transaction():
   self.store.lock();d=copy.deepcopy(self.get(ref));self.eligible(d);p=self.profile(d['account_ref'],d['channel'])
   if d['status']!='QUEUED' or d['reply']['creator_ref']!=self.actor or d['reply']['anchor_id']!=d['last_inbound_id'] or digest(p)!=d['reply']['profile_digest'] or not p['allow_reply']:raise CRMError('INBOX_NOT_DISPATCHABLE',409)
   if len(d['messages'])>=(99 if d['status']=='DISPATCHING' else 100):raise CRMError('INBOX_THREAD_MESSAGE_LIMIT',409)
   token=secrets.token_hex(32);d['claim_hash']=hashlib.sha256(token.encode()).hexdigest();d['claimed_at']=self.clock().isoformat();d['status']='DISPATCHING';self.emit(d,str(uuid.uuid4()),'worker_claim','worker',d['revision']);return d,p,token
 def dispatch(self,ref,client_factory=None):
  from .inbox_adapters import send
  d,p,token=self.claim(ref)
  with self.store.transaction():
   self.store.lock();self.authority(d['channel']);self.eligible(d)
   if self.raw(ref)['last_inbound_id']!=d['reply']['anchor_id'] or self.raw(ref)['claim_hash']!=d['claim_hash'] or digest(self.profile(d['account_ref'],d['channel']))!=d['reply']['profile_digest']:raise CRMError('INBOX_REVIEW_CHANGED',409)
   result=send(d,p,client_factory=client_factory)
  return self.finish(ref,token,result)
 def finish(self,ref,token,result):
  if not isinstance(result,dict) or set(result)!={'status','remote_id'} or result['status'] not in ('ACCEPTED','UNCERTAIN'):raise CRMError('INBOX_INVALID_TRANSPORT_RESULT')
  if result['status']=='ACCEPTED':remote_ref(result['remote_id'])
  with self.store.transaction():
   self.store.lock();d=copy.deepcopy(self.get(ref))
   if d['status']!='DISPATCHING' or not isinstance(token,str) or not hmac.compare_digest(d['claim_hash'],hashlib.sha256(token.encode()).hexdigest()):raise CRMError('INBOX_CLAIM_REQUIRED',409)
   d['status']=result['status'];d['claim_hash']=None;d['reply']['remote_id']=result['remote_id'];d['messages'].append({'direction':'OUT','body':d['reply']['text'],'remote_id':result['remote_id'],'anchor_id':d['reply']['anchor_id'],'status':result['status'],'occurred_at':self.clock().isoformat(),'delivery_verified':False});d['error_code']='NO_AUTOMATIC_RESEND' if result['status']=='UNCERTAIN' else None
   return self.emit(d,str(uuid.uuid4()),'worker_result','worker',d['revision'])
