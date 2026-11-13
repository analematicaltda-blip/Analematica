"""Own outbound SMS/MMS/WhatsApp jobs. No implicit channel or link fallback."""
import copy,hashlib,hmac,json,os,re,secrets,uuid,math
from datetime import datetime,timedelta,timezone
from .crm import CRMError,text,digest as base_digest,moment
from .opportunities import uuid_ref
from .contract import SYSTEM
from .email_campaigns import contact_ref
MAX_RECORDS=500
GSM_BASIC=set('@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ !"#¤%&\'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà')
GSM_EXTRA=set('^{}\\[~]|€\f')
def phone(value):
 if not isinstance(value,str) or not re.fullmatch(r'\+573[0-9]{9}',value):raise CRMError('MOBILE_CO_E164_REQUIRED')
 return value
def digest(value):
 try:return base_digest(value)
 except UnicodeError:raise CRMError('MOBILE_INVALID_TEXT') from None
def segments(value):
 if all(c in GSM_BASIC or c in GSM_EXTRA for c in value):
  units=sum(2 if c in GSM_EXTRA else 1 for c in value);return {'encoding':'GSM-7','units':units,'segments':1 if units<=160 else math.ceil(units/153)}
 try:units=len(value.encode('utf-16-le'))//2
 except UnicodeError:raise CRMError('MOBILE_INVALID_TEXT') from None
 return {'encoding':'UCS-2','units':units,'segments':1 if units<=70 else math.ceil(units/67)}
class MobileMessages:
 def __init__(self,store,crm=None,clock=None):self.store,self.crm=store,crm;self.actor=crm.actor if crm else 'SIGNED_MOBILE_ADAPTER';self.clock=clock or (lambda:datetime.now(timezone.utc))
 def key(self):return SYSTEM+':'+self.store.scope+':'+(getattr(self.store,'provider',None) or '-')
 def authority(self,channel=None):
  if not self.crm:raise CRMError('MOBILE_PRIVATE_AUTH_REQUIRED',403)
  access=self.crm.authorize();caps=access.session()['capability_permissions'];permission='campaign.whatsapp.multimedia.send' if channel=='WHATSAPP' else 'campaign.sms_mms.send'
  if not access.principal['is_manager'] or not (caps.get(permission) if channel else caps.get('campaign.sms_mms.send') or caps.get('campaign.whatsapp.multimedia.send')):raise CRMError('MOBILE_CHANNEL_PERMISSION_REQUIRED',403)
 def secret(self,name):
  try:
   key=json.loads(os.environ.get(name,'{}')).get(self.key())
   if not isinstance(key,str) or not 32<=len(key)<=256:raise ValueError()
   return key.encode()
  except (ValueError,TypeError,AttributeError):raise CRMError('MOBILE_SECRET_REQUIRED',503) from None
 def policy(self,channel):
  try:
   p=json.loads(os.environ.get('COMMERCIAL_MOBILE_POLICIES','{}')).get(self.key(),{}).get(channel)
   required={'version','adapter','from_id','credential_env','limit_daily','max_segments','estimate_minor','currency','co_support_digest','allow_dispatch','media_max_bytes','public_base_url','wa_template_name','wa_language','wa_template_digest','allow_sms_link','allowed_media_kinds','wa_header_kind','media_max_seconds','wa_template_body'}
   if channel not in ('SMS','MMS','WHATSAPP') or not isinstance(p,dict) or set(p)!=required:raise ValueError()
   if p['adapter']!=('meta-whatsapp' if channel=='WHATSAPP' else 'twilio-sms' if channel=='SMS' else 'twilio-mms') or type(p['allow_dispatch'])!=bool or type(p['allow_sms_link'])!=bool or p['currency']!='COP':raise ValueError()
   for k,lo,hi in [('limit_daily',1,100),('max_segments',1,10),('estimate_minor',0,10000000),('media_max_bytes',1024,16777216),('media_max_seconds',1,120)]:
    if type(p[k])!=int or not lo<=p[k]<=hi:raise ValueError()
   if not isinstance(p['allowed_media_kinds'],list) or len(p['allowed_media_kinds'])>2 or not all(k in ('IMAGE','VIDEO') for k in p['allowed_media_kinds']):raise ValueError()
   if not re.fullmatch('[a-f0-9]{64}',str(p['co_support_digest'])) or not re.fullmatch('COMMERCIAL_MOBILE_SECRET_[A-Z0-9_]{1,60}',str(p['credential_env'])):raise ValueError()
   text(p['version'],80)
   from urllib.parse import urlsplit
   u=urlsplit(p['public_base_url'])
   if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/') or u.port not in (None,443):raise ValueError()
   if channel=='WHATSAPP':
    if p['wa_header_kind'] not in ('IMAGE','VIDEO') or not isinstance(p['wa_template_body'],str) or p['wa_template_body'].count('{{body}}')!=1:raise ValueError()
    text(p['wa_template_body'],2000)
    if not re.fullmatch('[0-9]{1,30}',str(p['from_id'])) or not re.fullmatch('[a-z0-9_]{1,100}',str(p['wa_template_name'])) or not re.fullmatch('[a-z]{2}(?:_[A-Z]{2})?',str(p['wa_language'])) or not re.fullmatch('[a-f0-9]{64}',str(p['wa_template_digest'])):raise ValueError()
   elif not re.fullmatch(r'\+[1-9][0-9]{7,14}',str(p['from_id'])):raise ValueError()
   return p
  except (ValueError,TypeError,KeyError,AttributeError):raise CRMError('MOBILE_CHANNEL_POLICY_REQUIRED',503) from None
 def raw(self,ref):
  uuid_ref(ref);d=self.store.get(ref)
  if not d:raise CRMError('MOBILE_RECORD_NOT_FOUND',404)
  previous='0'*64;events=list(self.store.events(ref))
  for e in events:
   if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('MOBILE_HISTORY_REVIEW_REQUIRED',503)
   previous=e['event_digest']
  if not events or len(events)!=d['revision'] or previous!=d['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('MOBILE_INTEGRITY_REVIEW_REQUIRED',503)
  return d
 def get(self,ref):self.authority();d=self.raw(ref);self.authority(d.get('channel'));return d
 def list(self):
  self.authority();return {'jobs':[{k:d[k] for k in ('id','title','status','revision','created_at')} for d in self.records() if d['kind']=='MESSAGE'],'saving_sends_messages':False,'worker_enabled':os.environ.get('COMMERCIAL_MOBILE_WORKER_ENABLED')=='1','real_provider_qualified':False,'max_recipients':1,'opened_tracking':False}
 def records(self):
  rows=list(self.store.all_jobs())
  if len(rows)>MAX_RECORDS:raise CRMError('MOBILE_RECORD_LIMIT',409)
  return [self.raw(r['id']) for r in rows]
 def emit(self,d,rid,op,signature,expected):
  d['revision']=expected+1;d['updated_at']=self.clock().isoformat();receipt={'request_id':rid,'job_id':d['id'],'status':d['status'],'revision':d['revision'],'network_call_by_command':False}
  e={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':d['id'],'operation':op,'fingerprint':signature,'previous_event_digest':d.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in d.items() if k!='last_event_digest'}),'receipt':receipt,'created_at':self.clock().isoformat()};e['event_digest']=digest(e);d['last_event_digest']=e['event_digest'];self.store.save(d,expected);self.store.append(e);return receipt
 def history(self,ref):
  self.get(ref);return {'events':list(self.store.events(ref)),'history_verified':True}
 def receipt(self,rid):
  self.authority();uuid_ref(rid);e=self.store.event(rid)
  if not e or e.get('scope')!=self.store.scope or e.get('provider_ref')!=getattr(self.store,'provider',None) or e.get('actor')!=self.actor:raise CRMError('MOBILE_RECEIPT_NOT_FOUND',404)
  self.raw(e['item_id']);return e['receipt']|{'previous_receipt_only':True}
 def suppressed(self,channel,address):
  ref=str(uuid.uuid5(uuid.NAMESPACE_URL,self.key()+':'+channel+':'+address));return self.raw(ref) if self.store.get(ref) else None
 def suppress(self,d,reason,evidence=None):
  channel,address=d['channel'],d['phone'];old=self.suppressed(channel,address)
  if old:return
  ref=str(uuid.uuid5(uuid.NAMESPACE_URL,self.key()+':'+channel+':'+address));block={'id':ref,'code':ref,'title':'Exclusión por canal','kind':'SUPPRESSION','channel':channel,'phone':address,'status':'SUPPRESSED','reason':reason,'support_digest':evidence,'support_authenticity_verified':False,'revision':0,'created_at':self.clock().isoformat()};self.emit(block,str(uuid.uuid4()),'suppress',digest(block),0)
  for job in self.records():
   if job['kind']=='MESSAGE' and job['channel']==channel and job['phone']==address and job['status'] in ('DRAFT','REVIEWED','QUEUED'):
    job=copy.deepcopy(job);job['status']='SUPPRESSED';self.emit(job,str(uuid.uuid4()),'suppression_applied',digest({'suppression':ref}),job['revision'])
 def eligible(self,d):
  c=self.crm.get(d['contact_id']);consent=c.get('consents',{}).get(d['channel']+':MARKETING',{})
  return c.get('phone')==d['phone'] and c.get('status') not in ('WITHDRAWN','ARCHIVED','DUPLICATE') and consent.get('granted') is True and moment(consent['expires_at'])>self.clock() and digest(consent)==d['consent_digest'] and not self.suppressed(d['channel'],d['phone'])
 def media(self,d,p):
  ref=d['media_ref']
  if ref is None:return None
  from .library_api import service
  library=service(self.crm);item=library.get(ref['item_id']);v=next((v for v in item['versions'] if v['number']==ref['version']),None)
  if not v or v['delivery_sha256']!=ref['sha256'] or item['published_version']!=ref['version'] or v['media']['kind'] not in ('IMAGE','VIDEO'):raise CRMError('MOBILE_MEDIA_REVIEW_REQUIRED',409)
  if v['media']['kind'] not in p['allowed_media_kinds'] or d['channel']=='WHATSAPP' and v['media']['kind']!=p['wa_header_kind']:raise CRMError('MOBILE_TEMPLATE_OR_MEDIA_KIND_MISMATCH',409)
  if v['media']['kind']=='VIDEO' and (v['media'].get('duration_seconds') is None or v['media']['duration_seconds']>p['media_max_seconds']):raise CRMError('MOBILE_MEDIA_DURATION_LIMIT',413)
  raw,mime=library.bytes(ref['item_id'],ref['version'],'delivery',public=True)
  cap=min(p['media_max_bytes'],5*1024*1024 if v['media']['kind']=='IMAGE' else 16*1024*1024)
  if len(raw)>cap:raise CRMError('MOBILE_MEDIA_LIMIT',413)
  prefix='/api/v1/mi-negocio/comercial/unified/' if SYSTEM=='erp-tur' else '/api/v1/commercial-unified/'
  return {'url':p['public_base_url'].rstrip('/')+prefix+'media-library/'+ref['item_id']+'/'+str(ref['version'])+('/' if SYSTEM!='sga-cd' else ''),'kind':v['media']['kind'],'mime':mime,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'rights_authenticity_verified':False}
 def prepare(self,d,p):
  asset=self.media(d,p);body=d['body'];mode=d['mode']
  if d['channel']=='SMS' and mode=='TEXT_WITH_LINK':
   if not p['allow_sms_link'] or d['confirmed_link'] is not True or not asset:raise CRMError('MOBILE_LINK_AUTHORIZATION_REQUIRED',409)
   body+='\n'+asset['url']
  info=segments(body) if d['channel']=='SMS' else {'encoding':'PROVIDER_TEMPLATE' if d['channel']=='WHATSAPP' else 'MMS','units':len(body),'segments':1}
  if info['segments']>p['max_segments']:raise CRMError('MOBILE_SEGMENT_LIMIT',413)
  return {'body':body,'media':asset,'sender_ref':p['from_id'],'template':({'name':p['wa_template_name'],'language':p['wa_language'],'header_kind':p['wa_header_kind'],'declared_body_preview':p['wa_template_body'].replace('{{body}}',body),'support_digest':p['wa_template_digest'],'approval_authenticity_verified':False} if d['channel']=='WHATSAPP' else None),'length':info,'quote':{'currency':'COP','estimated_minor':info['segments']*p['estimate_minor'],'basis':'OPERATOR_ESTIMATE','actual_minor':None,'provider_quote_verified':False},'sms_contains_attachment':False,'fallback_selected':False,'provider_qualified':False}
 def command(self,body):
  self.authority()
  if not isinstance(body,dict) or set(body)!={'request_id','operation','job_id','expected_revision','data'} or type(body['expected_revision'])!=int or not 0<=body['expected_revision']<1000 or not isinstance(body['data'],dict):raise CRMError('MOBILE_INVALID_COMMAND')
  rid=uuid_ref(body['request_id']);op=body['operation'];data=body['data'];fingerprint=digest({'scope':self.store.scope,'provider':getattr(self.store,'provider',None),'actor':self.actor,'body':body})
  with self.store.transaction():
   self.authority();self.store.lock();prior=self.store.event(rid)
   if prior:
    self.receipt(rid)
    if prior.get('fingerprint')!=fingerprint:raise CRMError('MOBILE_REQUEST_CONFLICT',409)
    return self.receipt(rid)|{'replayed':True}
   if op=='create':
    if body['job_id'] is not None or body['expected_revision']!=0 or set(data)!={'title','channel','contact_id','body','mode','media_ref','confirmed_link'} or data['channel'] not in ('SMS','MMS','WHATSAPP') or type(data['confirmed_link'])!=bool:raise CRMError('MOBILE_INVALID_DRAFT')
    self.authority(data['channel']);p=self.policy(data['channel']);c=self.crm.get(contact_ref(data['contact_id']));address=phone(c.get('phone'));message=text(data['body'],1000)
    if re.search(r'https?://|www\.',message,re.I):raise CRMError('MOBILE_UNBOUND_LINK_REJECTED')
    if data['channel']=='SMS':
     if data['mode'] not in ('TEXT','TEXT_WITH_LINK') or (data['mode']=='TEXT')!=(data['media_ref'] is None):raise CRMError('MOBILE_SMS_HAS_NO_ATTACHMENTS')
    elif data['mode']!='MULTIMEDIA' or data['media_ref'] is None:raise CRMError('MOBILE_MULTIMEDIA_REQUIRED')
    ref=data['media_ref']
    if ref is not None:
     if not isinstance(ref,dict) or set(ref)!={'item_id','version','sha256'} or type(ref['version'])!=int or not 1<=ref['version']<=20 or not re.fullmatch('[a-f0-9]{64}',str(ref['sha256'])):raise CRMError('MOBILE_INVALID_MEDIA_REFERENCE')
     uuid_ref(ref['item_id'])
    if sum(j['kind']=='MESSAGE' for j in self.records())>=200:raise CRMError('MOBILE_JOB_LIMIT',409)
    ref=str(uuid.uuid4());d={'id':ref,'code':ref,'kind':'MESSAGE','title':text(data['title'],150),'channel':data['channel'],'contact_id':data['contact_id'],'phone':address,'body':message,'mode':data['mode'],'media_ref':copy.deepcopy(data['media_ref']),'confirmed_link':data['confirmed_link'],'creator_ref':self.actor,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'revision':0,'status':'DRAFT','created_at':self.clock().isoformat(),'consent_digest':digest(c.get('consents',{}).get(data['channel']+':MARKETING',{})),'policy_digest':digest(p),'review':None,'authorization':None,'attempts':0,'provider_message_id':None,'accepted_at':None,'sent_at':None,'delivered_at':None,'read_at':None,'actual_cost_minor':None,'error_code':None}
    d['prepared']=self.prepare(d,p)
   else:
    d=copy.deepcopy(self.get(uuid_ref(body['job_id'])))
    if d['kind']!='MESSAGE' or d['creator_ref']!=self.actor:raise CRMError('MOBILE_SAME_ADMIN_REQUIRED',403)
    if d['revision']!=body['expected_revision']:raise CRMError('MOBILE_REVISION_CONFLICT',409)
    if op=='review' and d['status']=='DRAFT' and data=={'confirmed_content':True,'confirmed_recipient':True} and all(type(v)==bool for v in data.values()):d['status']='REVIEWED';d['review']={'actor':self.actor,'request_id':rid}
    elif op=='queue' and d['status']=='REVIEWED' and set(data)=={'confirmed_impact','max_estimated_minor'} and data['confirmed_impact'] is True and type(data['max_estimated_minor'])==int:
     p=self.policy(d['channel'])
     if digest(p)!=d['policy_digest'] or not self.eligible(d):raise CRMError('MOBILE_CONSENT_OR_POLICY_CHANGED',409)
     current=self.prepare(d,p)
     if current!=d['prepared'] or data['max_estimated_minor']<current['quote']['estimated_minor']:raise CRMError('MOBILE_QUOTE_APPROVAL_REQUIRED',409)
     d['status']='QUEUED';d['authorization']={'actor':self.actor,'request_id':rid,'max_estimated_minor':data['max_estimated_minor']}
    elif op=='cancel' and not data and d['status'] in ('DRAFT','REVIEWED','QUEUED'):d['status']='CANCELLED'
    elif op=='suppress' and set(data)=={'evidence_digest'} and re.fullmatch('[a-f0-9]{64}',str(data['evidence_digest'])):
     self.suppress(d,'ADMIN_REPORTED_OPT_OUT',data['evidence_digest']);return self.emit(copy.deepcopy(self.raw(d['id'])),rid,op,fingerprint,self.raw(d['id'])['revision'])
    elif op=='recover' and not data and d['status']=='DISPATCHING' and moment(d['claimed_at'])+timedelta(minutes=15)<=self.clock():d['status']='UNCERTAIN';d['claim_hash']=None;d['error_code']='INTERRUPTED_NO_AUTO_RETRY'
    else:raise CRMError('MOBILE_STATE_REQUIRED',409)
   return self.emit(d,rid,op,fingerprint,body['expected_revision'])
 def claim(self,ref):
  self.authority()
  if os.environ.get('COMMERCIAL_MOBILE_WORKER_ENABLED')!='1':raise CRMError('MOBILE_WORKER_DISABLED',503)
  with self.store.transaction():
   self.store.lock();d=copy.deepcopy(self.get(ref));p=self.policy(d['channel'])
   if d['status']!='QUEUED' or d['creator_ref']!=self.actor or not p['allow_dispatch'] or digest(p)!=d['policy_digest']:raise CRMError('MOBILE_NOT_DISPATCHABLE',409)
   if not self.eligible(d):d['status']='SUPPRESSED';self.emit(d,str(uuid.uuid4()),'skip_ineligible','worker',d['revision']);return None
   prepared=self.prepare(d,p)
   if prepared!=d['prepared']:raise CRMError('MOBILE_QUOTE_OR_MEDIA_CHANGED',409)
   count=sum(1 for j in self.records() if j['kind']=='MESSAGE' and j['channel']==d['channel'] and j.get('claimed_at') and moment(j['claimed_at']).date()==self.clock().date())
   if count>=p['limit_daily']:raise CRMError('MOBILE_DAILY_QUOTA',429)
   token=secrets.token_hex(32);d['claim_hash']=hashlib.sha256(token.encode()).hexdigest();d['status']='DISPATCHING';d['attempts']=1;d['claimed_at']=self.clock().isoformat();self.emit(d,str(uuid.uuid4()),'dispatch_claim','worker',d['revision']);return d,p,token,prepared
 def finish(self,ref,token,status,provider_id=None):
  self.authority()
  if status not in ('ACCEPTED','REJECTED','UNCERTAIN','SUPPRESSED'):raise CRMError('MOBILE_TRANSPORT_STATUS_INVALID')
  with self.store.transaction():
   self.store.lock();d=copy.deepcopy(self.get(ref))
   if d['status']!='DISPATCHING' or not hmac.compare_digest(d['claim_hash'],hashlib.sha256(token.encode()).hexdigest()):raise CRMError('MOBILE_DISPATCH_REVIEW_REQUIRED',409)
   if status=='ACCEPTED' and (not isinstance(provider_id,str) or not 1<=len(provider_id)<=200):raise CRMError('MOBILE_PROVIDER_ID_REQUIRED')
   d['status']=status;d['provider_message_id']=provider_id;d['accepted_at']=self.clock().isoformat() if status=='ACCEPTED' else None;d['claim_hash']=None;d['error_code']='TRANSPORT_UNKNOWN_NO_AUTO_RETRY' if status=='UNCERTAIN' else None;return self.emit(d,str(uuid.uuid4()),'transport_result','worker',d['revision'])
 def provider_receipt(self,body,signature):
  if not isinstance(body,dict) or set(body)!={'event_id','job_id','provider_message_id','status','occurred_at'} or body['status'] not in ('SENT','DELIVERED','FAILED','OPT_OUT','READ'):raise CRMError('MOBILE_PROVIDER_EVENT_INVALID')
  expected=hmac.new(self.secret('COMMERCIAL_MOBILE_RECEIPT_KEYS'),digest(body).encode(),hashlib.sha256).hexdigest()
  if not isinstance(signature,str) or not hmac.compare_digest(expected,signature):raise CRMError('MOBILE_PROVIDER_SIGNATURE_REJECTED',401)
  rid=uuid_ref(body['event_id']);fingerprint=digest(body)
  with self.store.transaction():
   self.store.lock();old=self.store.event(rid)
   if old:
    if old.get('scope')!=self.store.scope or old.get('provider_ref')!=getattr(self.store,'provider',None) or old.get('fingerprint')!=fingerprint:raise CRMError('MOBILE_PROVIDER_EVENT_CONFLICT',409)
    self.raw(old['item_id']);return {'recorded':True,'replayed':True}
   d=copy.deepcopy(self.raw(uuid_ref(body['job_id'])));stamp=moment(body['occurred_at'])
   if stamp>self.clock()+timedelta(minutes=5) or stamp<moment(d['created_at']):raise CRMError('MOBILE_PROVIDER_TIMESTAMP_REJECTED',409)
   if body['status']=='OPT_OUT':
    self.emit(d,rid,'provider_opt_out',fingerprint,d['revision']);self.suppress(d,'SIGNED_ADAPTER_OPT_OUT',fingerprint);return {'recorded':True,'provider_report_only':True}
   if body['status']=='READ' and d['channel']!='WHATSAPP':raise CRMError('MOBILE_READ_NOT_SUPPORTED',409)
   if d['status'] not in ('ACCEPTED','SENT','DELIVERED') or not body['provider_message_id'] or d['provider_message_id']!=body['provider_message_id']:raise CRMError('MOBILE_PROVIDER_EVENT_MISMATCH',409)
   if d['status']=='DELIVERED' and body['status']!='READ':raise CRMError('MOBILE_PROVIDER_ORDER_REVIEW_REQUIRED',409)
   d['status']=body['status'];d['receipt_source']='SIGNED_ADAPTER_REPORT';d['provider_authenticity_qualified']=False
   if body['status']=='SENT':d['sent_at']=stamp.isoformat()
   if body['status']=='DELIVERED':d['delivered_at']=stamp.isoformat()
   if body['status']=='READ':d['read_at']=stamp.isoformat()
   return self.emit(d,rid,'provider_report',fingerprint,d['revision'])
