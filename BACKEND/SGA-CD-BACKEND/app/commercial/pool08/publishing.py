"""Durable publication calendar. Human commands never perform network operations.

A transport acknowledgement is not publication proof. Live provider adapters remain
unqualified: this module deliberately contains no network call or public receipt API.
"""
import copy, hashlib, hmac, os, re, secrets, uuid
from datetime import datetime, timedelta, timezone
from .crm import CRMError, text, digest as base_digest, moment
from .opportunities import uuid_ref
from .contract import SYSTEM
def digest(value):
 try:return base_digest(value)
 except UnicodeError:raise CRMError('PUBLISH_INVALID_TEXT') from None
MAX_RECORDS=500
FORMATS={'FACEBOOK_PHOTO':'IMAGE','INSTAGRAM_REEL':'VIDEO','YOUTUBE_VIDEO':'VIDEO','TIKTOK_VIDEO':'VIDEO'}
class Publishing:
 def __init__(self,store,crm,clock=None):
  self.store,self.crm=store,crm;self.actor=crm.actor;self.clock=clock or (lambda:datetime.now(timezone.utc))
 def authority(self):
  access=self.crm.authorize()
  if not access.principal['is_manager'] or not access.session()['capability_permissions'].get('channel.video.publish'):raise CRMError('PUBLISH_PERMISSION_REQUIRED',403)
 def raw(self,ref):
  uuid_ref(ref);d=self.store.get(ref)
  if not d:raise CRMError('PUBLISH_RECORD_NOT_FOUND',404)
  previous='0'*64;events=list(self.store.events(ref))
  for e in events:
   if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('PUBLISH_HISTORY_REVIEW_REQUIRED',503)
   previous=e['event_digest']
  if not events or len(events)!=d['revision'] or previous!=d['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('PUBLISH_INTEGRITY_REVIEW_REQUIRED',503)
  return d
 def get(self,ref):self.authority();d=self.raw(ref);self.authority();return d
 def list(self):
  self.authority();return {'jobs':[{k:d[k] for k in ('id','title','status','revision','created_at')} for d in self.records() if d['kind']=='PUBLICATION'],'saving_publishes':False,'worker_enabled':os.environ.get('COMMERCIAL_PUBLISH_WORKER_ENABLED')=='1','real_provider_qualified':False,'account_ownership_verified':False,'supported_formats':list(FORMATS)}
 def records(self):
  rows=list(self.store.all_jobs())
  if len(rows)>MAX_RECORDS:raise CRMError('PUBLISH_RECORD_LIMIT',409)
  return [self.raw(r['id']) for r in rows]
 def emit(self,d,rid,op,signature,expected):
  d['revision']=expected+1;d['updated_at']=self.clock().isoformat();receipt={'request_id':rid,'job_id':d['id'],'status':d['status'],'revision':d['revision'],'network_call_by_command':op.startswith('worker_')}
  e={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':d['id'],'operation':op,'fingerprint':signature,'previous_event_digest':d.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in d.items() if k!='last_event_digest'}),'receipt':receipt,'created_at':self.clock().isoformat()};e['event_digest']=digest(e);d['last_event_digest']=e['event_digest'];self.store.save(d,expected);self.store.append(e);return receipt
 def history(self,ref):
  self.get(ref);return {'events':list(self.store.events(ref)),'history_verified':True}
 def receipt(self,rid):
  self.authority();uuid_ref(rid);e=self.store.event(rid)
  if not e or e.get('scope')!=self.store.scope or e.get('provider_ref')!=getattr(self.store,'provider',None) or e.get('actor')!=self.actor:raise CRMError('PUBLISH_RECEIPT_NOT_FOUND',404)
  self.raw(e['item_id']);return e['receipt']|{'previous_receipt_only':True}

 def asset(self,ref,format):
  if not isinstance(ref,dict) or set(ref)!={'item_id','version','sha256'} or type(ref['version'])!=int or not 1<=ref['version']<=20 or not isinstance(ref['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',ref['sha256']):raise CRMError('PUBLISH_INVALID_ASSET')
  uuid_ref(ref['item_id'])
  from .library_api import service
  lib=service(self.crm);item=lib.get(ref['item_id']);version=next((v for v in item['versions'] if v['number']==ref['version']),None)
  if not version or item['published_version']!=ref['version'] or version['delivery_sha256']!=ref['sha256'] or version['media']['kind']!=FORMATS[format]:raise CRMError('PUBLISH_ASSET_REVIEW_REQUIRED',409)
  raw,mime=lib.bytes(ref['item_id'],ref['version'],'delivery',public=True)
  if len(raw)>(5*1024*1024 if FORMATS[format]=='IMAGE' else 16*1024*1024) or hashlib.sha256(raw).hexdigest()!=ref['sha256']:raise CRMError('PUBLISH_ASSET_LIMIT_OR_DIGEST',409)
  media=version['media']
  if FORMATS[format]=='VIDEO' and (mime!='video/mp4' or not isinstance(media.get('duration_seconds'),(int,float)) or not 0<media['duration_seconds']<=120):raise CRMError('PUBLISH_VIDEO_PROFILE_REQUIRED',409)
  if format=='INSTAGRAM_REEL' and (media['duration_seconds']<3 or media.get('width',0)*16!=media.get('height',0)*9 or media.get('width',0)<720):raise CRMError('PUBLISH_VERTICAL_REEL_REQUIRED',409)
  return {'sha256':ref['sha256'],'mime':mime,'bytes':len(raw),'kind':media['kind'],'duration_seconds':media.get('duration_seconds'),'rights_authenticity_verified':False}
 def command(self,body):
  self.authority()
  if not isinstance(body,dict) or set(body)!={'request_id','operation','job_id','expected_revision','data'} or type(body['expected_revision'])!=int or not 0<=body['expected_revision']<1000 or not isinstance(body['data'],dict):raise CRMError('PUBLISH_INVALID_COMMAND')
  rid=uuid_ref(body['request_id']);op=body['operation'];data=body['data'];signature=digest({'scope':self.store.scope,'provider':getattr(self.store,'provider',None),'actor':self.actor,'body':body})
  with self.store.transaction():
   self.authority();self.store.lock();prior=self.store.event(rid)
   if prior:
    self.receipt(rid)
    if prior.get('fingerprint')!=signature:raise CRMError('PUBLISH_REQUEST_CONFLICT',409)
    return self.receipt(rid)|{'replayed':True}
   if op=='create':
    if body['job_id'] is not None or body['expected_revision']!=0 or set(data)!={'title','caption','format','account_ref','visibility','media_ref','disclosure'} or not isinstance(data['format'],str) or data['format'] not in FORMATS or data['visibility'] not in ('PUBLIC','PRIVATE','UNLISTED') or data['disclosure']!='NONE':raise CRMError('PUBLISH_INVALID_DRAFT')
    if data['visibility']=='UNLISTED' and data['format']!='YOUTUBE_VIDEO' or data['visibility']=='PRIVATE' and data['format'] in ('FACEBOOK_PHOTO','INSTAGRAM_REEL'):raise CRMError('PUBLISH_VISIBILITY_UNSUPPORTED')
    # Account refs are private references only, not OAuth ownership verification.
    account=text(data['account_ref'],100)
    if not re.fullmatch('[A-Za-z0-9_-]{1,100}',account):raise CRMError('PUBLISH_INVALID_ACCOUNT')
    if len(self.records())>=200:raise CRMError('PUBLISH_JOB_LIMIT',409)
    ref=str(uuid.uuid4());d={'id':ref,'code':ref,'kind':'PUBLICATION','title':text(data['title'],100),'caption':text(data['caption'],2000),'format':data['format'],'account_ref':account,'visibility':data['visibility'],'disclosure':data['disclosure'],'media_ref':copy.deepcopy(data['media_ref']),'creator_ref':self.actor,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'revision':0,'status':'DRAFT','created_at':self.clock().isoformat(),'scheduled_at':None,'review':None,'authorization':None,'attempts':0,'remote_id':None,'published_at':None,'error_code':None,'account_ownership_verified':False,'live_adapter_qualified':False}
    d['asset_snapshot']=self.asset(d['media_ref'],d['format'])
   else:
    d=copy.deepcopy(self.get(uuid_ref(body['job_id'])))
    if d['creator_ref']!=self.actor:raise CRMError('PUBLISH_SAME_ADMIN_REQUIRED',403)
    if d['revision']!=body['expected_revision']:raise CRMError('PUBLISH_REVISION_CONFLICT',409)
    if op=='review' and d['status']=='DRAFT' and data=={'confirmed_content':True,'confirmed_account':True} and all(type(v)==bool for v in data.values()):
     if self.asset(d['media_ref'],d['format'])!=d['asset_snapshot']:raise CRMError('PUBLISH_ASSET_CHANGED',409)
     d['status']='REVIEWED';d['review']={'actor':self.actor,'request_id':rid}
    elif op=='schedule' and d['status']=='REVIEWED' and set(data)=={'confirmed_impact','scheduled_at'} and data['confirmed_impact'] is True:
     when=moment(data['scheduled_at'])
     if not self.clock()<=when<=self.clock()+timedelta(days=30):raise CRMError('PUBLISH_SCHEDULE_RANGE')
     if self.asset(d['media_ref'],d['format'])!=d['asset_snapshot']:raise CRMError('PUBLISH_ASSET_CHANGED',409)
     p=self.profile(d);d['profile_digest']=digest(p)
     d['scheduled_at']=when.astimezone(timezone.utc).isoformat();d['status']='SCHEDULED';d['authorization']={'actor':self.actor,'request_id':rid,'visibility':d['visibility']}
    elif op=='recover' and not data and d['status']=='DISPATCHING' and moment(d['claimed_at'])+timedelta(minutes=15)<=self.clock():
     d['status']='UNCERTAIN' if d['claimed_from'] in ('SCHEDULED','READY_TO_PUBLISH') else 'REMOTE_REVIEW';d['claim_hash']=None;d['next_poll_at']=None;d['error_code']='INTERRUPTED_NO_AUTOMATIC_REUPLOAD'
    elif op=='cancel' and not data and d['status'] in ('DRAFT','REVIEWED','SCHEDULED'):d['status']='CANCELLED'
    else:raise CRMError('PUBLISH_STATE_REQUIRED',409)
   return self.emit(d,rid,op,signature,body['expected_revision'])
 def due(self,limit=20):
  self.authority()
  if type(limit)!=int or not 1<=limit<=50:raise CRMError('PUBLISH_BATCH_LIMIT')
  # Filter before limiting: later UUIDs must not starve due work.
  jobs=[d for d in self.records() if d['status']=='SCHEDULED' and moment(d['scheduled_at'])<=self.clock()]
  return sorted(jobs,key=lambda d:(d['scheduled_at'],d['id']))[:limit]
 def key(self):return SYSTEM+':'+self.store.scope+':'+(getattr(self.store,'provider',None) or '-')
 def profile(self,d):
  import json
  from urllib.parse import urlsplit
  try:
   p=json.loads(os.environ.get('COMMERCIAL_PUBLISH_ACCOUNTS','{}'))[self.key()][d['account_ref']]
   if not isinstance(p,dict) or set(p)!={'version','format','account_id','page_id','credential_env','public_base_url','allow_publish','ownership_support_digest','daily_limit'}:raise ValueError()
   if p['format']!=d['format'] or type(p['allow_publish'])!=bool or type(p['daily_limit'])!=int or not 1<=p['daily_limit']<=50:raise ValueError()
   if not re.fullmatch('COMMERCIAL_PUBLISH_SECRET_[A-Z0-9_]{1,60}',str(p['credential_env'])) or not re.fullmatch('[a-f0-9]{64}',str(p['ownership_support_digest'])):raise ValueError()
   text(p['version'],80)
   if not re.fullmatch('[A-Za-z0-9_-]{1,100}',str(p['account_id'])):raise ValueError()
   if d['format']=='INSTAGRAM_REEL' and not re.fullmatch('[0-9]{1,40}',str(p['page_id'])):raise ValueError()
   u=urlsplit(p['public_base_url'])
   if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/') or u.port not in (None,443):raise ValueError()
   return copy.deepcopy(p)
  except (ValueError,TypeError,KeyError,AttributeError):raise CRMError('PUBLISH_ACCOUNT_PROFILE_REQUIRED',503) from None
 def media_url(self,d,p):
  prefix='/api/v1/mi-negocio/comercial/unified/' if SYSTEM=='erp-tur' else '/api/v1/commercial-unified/'
  ref=d['media_ref'];return p['public_base_url'].rstrip('/')+prefix+'media-library/'+ref['item_id']+'/'+str(ref['version'])+('/' if SYSTEM!='sga-cd' else '')
 def claim(self,ref):
  self.authority()
  if os.environ.get('COMMERCIAL_PUBLISH_WORKER_ENABLED')!='1' or os.environ.get('COMMERCIAL_PUBLISH_NETWORK_ENABLED')!='1':raise CRMError('PUBLISH_WORKER_DISABLED',503)
  with self.store.transaction():
   self.store.lock();d=copy.deepcopy(self.get(ref))
   if d['creator_ref']!=self.actor:raise CRMError('PUBLISH_SAME_ADMIN_REQUIRED',403)
   current=d['status'];mutation=current in ('SCHEDULED','READY_TO_PUBLISH')
   if current not in ('SCHEDULED','READY_TO_PUBLISH','WAIT_CONTAINER','VERIFY','REMOTE_REVIEW'):raise CRMError('PUBLISH_NOT_DISPATCHABLE',409)
   if current=='SCHEDULED' and moment(d['scheduled_at'])>self.clock() or d.get('next_poll_at') and moment(d['next_poll_at'])>self.clock():raise CRMError('PUBLISH_NOT_DUE',409)
   p=self.profile(d)
   if not p['allow_publish'] or digest(p)!=d.get('profile_digest'):raise CRMError('PUBLISH_PROFILE_CHANGED_OR_DISABLED',409)
   if mutation:
    if moment(d['scheduled_at'])+timedelta(days=7)<self.clock():raise CRMError('PUBLISH_AUTH_EXPIRED',409)
    if self.asset(d['media_ref'],d['format'])!=d['asset_snapshot']:raise CRMError('PUBLISH_ASSET_CHANGED',409)
    if current=='SCHEDULED':
     count=sum(j.get('started_at') is not None and moment(j['started_at']).date()==self.clock().date() and j['account_ref']==d['account_ref'] for j in self.records())
     if count>=p['daily_limit']:raise CRMError('PUBLISH_DAILY_LIMIT',429)
   elif d.get('polls',0)>=60:raise CRMError('PUBLISH_POLL_LIMIT_REVIEW_REQUIRED',409)
   token=secrets.token_hex(32);d['claim_hash']=hashlib.sha256(token.encode()).hexdigest();d['claimed_at']=self.clock().isoformat();d['claimed_from']=current;d['status']='DISPATCHING';d['attempts']+=int(mutation)
   if current=='SCHEDULED':d['started_at']=self.clock().isoformat()
   if not mutation:d['polls']=d.get('polls',0)+1
   self.emit(d,str(uuid.uuid4()),'worker_claim','worker',d['revision']);return d,p,token
 def finish(self,ref,token,result):
  self.authority()
  allowed={'WAIT_CONTAINER','READY_TO_PUBLISH','VERIFY','PUBLISHED','REMOTE_PRIVATE','FAILED','UNCERTAIN','REMOTE_REVIEW'}
  if not isinstance(result,dict) or set(result)!={'status','remote_id','container_id','proof'} or result['status'] not in allowed:raise CRMError('PUBLISH_INVALID_TRANSPORT_RESULT')
  # Only the private worker calls this method; no route accepts provider results.
  if result['status'] in ('PUBLISHED','REMOTE_PRIVATE') and not result['proof']:raise CRMError('PUBLISH_REMOTE_READ_PROOF_REQUIRED')
  with self.store.transaction():
   self.store.lock();d=copy.deepcopy(self.get(ref))
   if d['status']!='DISPATCHING' or not isinstance(token,str) or not hmac.compare_digest(d['claim_hash'],hashlib.sha256(token.encode()).hexdigest()):raise CRMError('PUBLISH_CLAIM_REQUIRED',409)
   d['status']=result['status'];d['claim_hash']=None
   for k in ('remote_id','container_id'):
    if result[k] is not None:d[k]=result[k]
   d['remote_proof']=result['proof'];d['published_at']=self.clock().isoformat() if d['status']=='PUBLISHED' else None
   d['next_poll_at']=(self.clock()+timedelta(seconds=30)).isoformat() if d['status'] in ('WAIT_CONTAINER','VERIFY') else None
   d['error_code']='NO_AUTOMATIC_REUPLOAD' if d['status']=='UNCERTAIN' else None
   return self.emit(d,str(uuid.uuid4()),'worker_result','worker',d['revision'])
 def dispatch(self,ref,client_factory=None):
  from .publishing_adapters import step
  initial=self.get(ref);raw=None
  if initial['status']=='SCHEDULED' and initial['format']=='YOUTUBE_VIDEO':
   from .library_api import service
   raw,_=service(self.crm).bytes(initial['media_ref']['item_id'],initial['media_ref']['version'],'delivery',public=True)
  claimed=self.claim(ref);d,p,token=claimed
  with self.store.transaction():
   self.store.lock();self.authority();current=self.raw(ref)
   if current['status']!='DISPATCHING' or current['claim_hash']!=d['claim_hash'] or digest(self.profile(d))!=d['profile_digest']:raise CRMError('PUBLISH_CLAIM_OR_PROFILE_CHANGED',409)
   if d['claimed_from'] in ('SCHEDULED','READY_TO_PUBLISH') and self.asset(d['media_ref'],d['format'])!=d['asset_snapshot']:raise CRMError('PUBLISH_ASSET_CHANGED',409)
   result=step(d,p,self.media_url(d,p),raw=raw,client_factory=client_factory)
  return self.finish(ref,token,result)
