"""Own, bounded campaign drafts and delivery ledger. Saving never sends mail."""
import copy,hashlib,hmac,html,json,os,re,secrets,uuid
from datetime import datetime,timedelta,timezone
from .crm import CRMError,text,digest,moment
from .opportunities import uuid_ref
from .contract import SYSTEM
MAX_RECORDS=6000
class EmailCampaigns:
 def __init__(self,store,crm=None,clock=None):self.store,self.crm=store,crm;self.actor=crm.actor if crm else 'PUBLIC_UNSUBSCRIBE';self.clock=clock or (lambda:datetime.now(timezone.utc))
 def authority(self):
  if self.crm is None:raise CRMError('EMAIL_PRIVATE_AUTH_REQUIRED',403)
  a=self.crm.authorize()
  if not a.principal['is_manager'] or not a.session()['capability_permissions'].get('campaign.email.bulk.send'):raise CRMError('EMAIL_CAMPAIGN_MANAGER_REQUIRED',403)
 def key(self):return SYSTEM+':'+self.store.scope+':'+(getattr(self.store,'provider',None) or '-')
 def policy(self):
  try:
   p=json.loads(os.environ.get('COMMERCIAL_EMAIL_POLICIES','{}')).get(self.key())
   if not isinstance(p,dict) or set(p)!={'version','sender_email','sender_name','postal_address','public_base_url','daily_limit','consent_reviewed','allow_dispatch','smtp_host','smtp_port'} or p['smtp_host'] not in ('localhost','127.0.0.1') or (type(p['smtp_port'])!=int or p['smtp_port']!=1025) or type(p['daily_limit'])!=int or not 1<=p['daily_limit']<=100 or p['consent_reviewed'] is not True or type(p['allow_dispatch'])!=bool:raise ValueError()
   from urllib.parse import urlsplit
   u=urlsplit(p['public_base_url'])
   if u.scheme not in ('http','https') or not u.netloc or u.username or u.password or u.path not in ('','/') or u.query or u.fragment or u.scheme=='http' and u.hostname not in ('localhost','127.0.0.1'):raise ValueError()
   for k in ['version','sender_name','postal_address']:text(p[k],200)
   email(p['sender_email']);return p
  except (ValueError,TypeError,AttributeError,KeyError):raise CRMError('EMAIL_SENDER_POLICY_REQUIRED',503) from None
 def secret(self,name):
  try:
   v=json.loads(os.environ.get(name,'{}')).get(self.key())
   if not isinstance(v,str) or not 32<=len(v)<=256:raise ValueError()
   return v.encode()
  except (ValueError,TypeError,AttributeError):raise CRMError('EMAIL_SECRET_CONFIGURATION_REQUIRED',503) from None
 def raw(self,ref):
  uuid_ref(ref);d=self.store.get(ref)
  if not d:raise CRMError('EMAIL_RECORD_NOT_FOUND',404)
  previous='0'*64;events=list(self.store.events(ref))
  for e in events:
   if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('EMAIL_HISTORY_REVIEW_REQUIRED',503)
   previous=e['event_digest']
  if not events or len(events)!=d['revision'] or previous!=d['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('EMAIL_INTEGRITY_REVIEW_REQUIRED',503)
  return d
 def get(self,ref):self.authority();return self.raw(ref)
 def list(self):
  self.authority();return {'campaigns':[{k:d[k] for k in ('id','title','status','revision','created_at')} for d in self.records() if d['kind']=='CAMPAIGN'],'saving_sends_mail':False,'worker_enabled':os.environ.get('COMMERCIAL_EMAIL_WORKER_ENABLED')=='1','real_provider_qualified':False,'max_recipients':100,'opened_tracking':False}
 def records(self):
  rows=list(self.store.all_jobs())
  if len(rows)>MAX_RECORDS:raise CRMError('EMAIL_RECORD_LIMIT',409)
  return [self.raw(r['id']) for r in rows]
 def emit(self,d,rid,op,signature,expected):
  d['revision']=expected+1;d['updated_at']=self.clock().isoformat();receipt={'campaign_id':d['id'],'status':d['status'],'revision':d['revision'],'mail_sent_by_command':False}
  e={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':d['id'],'operation':op,'fingerprint':signature,'previous_event_digest':d.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in d.items() if k!='last_event_digest'}),'receipt':receipt,'created_at':self.clock().isoformat()};e['event_digest']=digest(e);d['last_event_digest']=e['event_digest'];self.store.save(d,expected);self.store.append(e);return receipt
 def receipt(self,rid):
  self.authority();uuid_ref(rid);e=self.store.event(rid)
  if not e or e.get('scope')!=self.store.scope or e.get('provider_ref')!=getattr(self.store,'provider',None) or e.get('actor')!=self.actor:raise CRMError('EMAIL_RECEIPT_NOT_FOUND',404)
  self.raw(e['item_id']);return e['receipt']|{'previous_receipt_only':True}
 def suppressed(self,address):
  ref=str(uuid.uuid5(uuid.NAMESPACE_URL,self.key()+':suppression:'+email(address)))
  return self.raw(ref) if self.store.get(ref) else None
 def suppress(self,address,reason,evidence_digest=None):
  old=self.suppressed(address)
  if old:return
  if len(list(self.store.all_jobs()))>=MAX_RECORDS:raise CRMError('EMAIL_RECORD_LIMIT',409)
  ref=str(uuid.uuid5(uuid.NAMESPACE_URL,self.key()+':suppression:'+email(address)));d={'id':ref,'code':'suppression:'+hashlib.sha256(email(address).encode()).hexdigest(),'kind':'SUPPRESSION','title':'Exclusión de correo','status':'SUPPRESSED','revision':0,'address':email(address),'reason':reason,'support_digest':evidence_digest,'support_authenticity_verified':False,'created_at':self.clock().isoformat()};self.emit(d,str(uuid.uuid4()),'suppress',digest({'address':address,'reason':reason}),0)
  for d in self.records():
   if d['kind']!='CAMPAIGN':continue
   d=copy.deepcopy(d);changed=False
   for r in d['recipients']:
    if r['email']==email(address) and r['status']=='PENDING':r['status']='SUPPRESSED';changed=True
   if changed and d['status']=='SCHEDULED' and all(r['status'] not in ('PENDING','DISPATCHING') for r in d['recipients']):d['status']='PROCESSED'
   if changed:self.emit(d,str(uuid.uuid4()),'suppression_applied',digest({'suppression_id':ref}),d['revision'])
 def eligible(self,contact,address):
  if not self.crm:return False
  c=self.crm.get(contact);p=c.get('consents',{}).get('EMAIL:MARKETING',{})
  try:current=email(c.get('email',''))
  except CRMError:return False
  return c.get('status') not in ('WITHDRAWN','ARCHIVED','DUPLICATE') and current==address and p.get('granted') is True and moment(p['expires_at'])>self.clock()
 def command(self,body):
  self.authority()
  if not isinstance(body,dict) or set(body)!={'request_id','operation','campaign_id','expected_revision','data'} or type(body['expected_revision'])!=int or not 0<=body['expected_revision']<1000 or not isinstance(body['data'],dict):raise CRMError('INVALID_EMAIL_CAMPAIGN_COMMAND')
  rid=uuid_ref(body['request_id']);op=body['operation'];values=body['data'];signature=digest({'domain':'EMAIL_CAMPAIGN','scope':self.store.scope,'provider':getattr(self.store,'provider',None),'actor':self.actor,'body':body})
  with self.store.transaction():
   self.authority();self.store.lock();prior=self.store.event(rid)
   if prior:
    self.receipt(rid)
    if prior.get('fingerprint')!=signature:raise CRMError('EMAIL_REQUEST_CONFLICT',409)
    return self.receipt(rid)|{'replayed':True}
   if op=='create':
    if body['campaign_id'] is not None or body['expected_revision']!=0 or set(values)!={'title','subject','body_text','template','contact_ids','exclude_contact_ids','segment'} or values['template'] not in ('LETTER','NOTICE') or not isinstance(values['contact_ids'],list) or not 1<=len(values['contact_ids'])<=100 or not all(isinstance(v,str) for v in values['contact_ids']) or len(set(values['contact_ids']))!=len(values['contact_ids']) or not isinstance(values['exclude_contact_ids'],list) or not all(isinstance(v,str) for v in values['exclude_contact_ids']) or not set(values['exclude_contact_ids'])<=set(values['contact_ids']) or not isinstance(values['segment'],str):raise CRMError('INVALID_EMAIL_CAMPAIGN_DRAFT')
    if sum(d['kind']=='CAMPAIGN' for d in self.records())>=50:raise CRMError('EMAIL_CAMPAIGN_LIMIT',409)
    subject=text(values['subject'],150)
    if any(ord(c)<32 for c in subject):raise CRMError('EMAIL_HEADER_CONTROL_REJECTED')
    body_text=text(values['body_text'],3000);validate_template(subject);validate_template(body_text);recipients=[];seen=set()
    for ref in values['contact_ids']:
     c=self.crm.get(contact_ref(ref));address=email(c['email']);state='EXCLUDED' if ref in values['exclude_contact_ids'] or address in seen else 'SUPPRESSED' if self.suppressed(address) else 'PENDING' if self.eligible(ref,address) else 'NO_CONSENT';seen.add(address);recipients.append({'contact_id':ref,'email':address,'name':text(c['name'],150),'status':state,'consent_digest':digest(c.get('consents',{}).get('EMAIL:MARKETING',{})),'attempts':0,'message_id':None,'accepted_at':None,'sent_at':None,'delivered_at':None,'opened_at':None,'error_code':None})
    ref=str(uuid.uuid4());d={'id':ref,'code':ref,'kind':'CAMPAIGN','scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'title':text(values['title'],150),'subject':subject,'body_text':body_text,'template':values['template'],'segment':text(values['segment'],100,True),'recipients':recipients,'creator_ref':self.actor,'status':'DRAFT','revision':0,'created_at':self.clock().isoformat(),'review':None,'authorization':None,'scheduled_at':None,'sender_policy_digest':None,'opened_tracking':False}
   else:
    d=copy.deepcopy(self.get(uuid_ref(body['campaign_id'])))
    if d['kind']!='CAMPAIGN' or d['revision']!=body['expected_revision']:raise CRMError('EMAIL_CAMPAIGN_REVISION_CONFLICT',409)
    if d['creator_ref']!=self.actor:raise CRMError('EMAIL_SAME_ADMINISTRATOR_REQUIRED',403)
    if op=='review' and d['status']=='DRAFT' and values=={'confirmed_content':True,'confirmed_audience':True} and all(type(v)==bool for v in values.values()):d['review']={'actor':self.actor,'request_id':rid,'at':self.clock().isoformat()};d['status']='REVIEWED'
    elif op=='schedule' and d['status']=='REVIEWED' and set(values)=={'confirmed_impact','scheduled_at'} and values['confirmed_impact'] is True:
     if not any(r['status']=='PENDING' for r in d['recipients']):raise CRMError('EMAIL_NO_ELIGIBLE_RECIPIENTS',409)
     scheduled=moment(values['scheduled_at']);p=self.policy();self.secret('COMMERCIAL_EMAIL_LINK_KEYS')
     if not self.clock()-timedelta(seconds=10)<=scheduled<=self.clock()+timedelta(days=30):raise CRMError('EMAIL_INVALID_SCHEDULE')
     d['authorization']={'actor':self.actor,'request_id':rid,'at':self.clock().isoformat()};d['scheduled_at']=scheduled.astimezone(timezone.utc).isoformat();d['sender_policy_digest']=digest(p);d['status']='SCHEDULED'
    elif op=='recover' and set(values)=={'contact_id'}:
     r=next((r for r in d['recipients'] if r['contact_id']==values['contact_id']),None)
     if not r or r['status']!='DISPATCHING' or moment(r['claimed_at'])+timedelta(minutes=15)>self.clock():raise CRMError('EMAIL_DISPATCH_REVIEW_REQUIRED',409)
     r['status']='UNCERTAIN';r['claim_hash']=None;r['error_code']='WORKER_INTERRUPTED_NO_AUTO_RETRY'
    elif op=='cancel' and not values and d['status'] in ('DRAFT','REVIEWED','SCHEDULED'):
     for r in d['recipients']:
      if r['status']=='PENDING':r['status']='CANCELLED'
     d['status']='CANCELLED'
    elif op=='suppress' and set(values)=={'contact_id','reason','evidence_digest'} and values['reason'] in ('UNSUBSCRIBED','BOUNCE_REPORTED') and re.fullmatch('[a-f0-9]{64}',str(values['evidence_digest'])):
     r=next((r for r in d['recipients'] if r['contact_id']==values['contact_id']),None)
     if not r:raise CRMError('EMAIL_RECIPIENT_NOT_FOUND',404)
     self.suppress(r['email'],values['reason'],values['evidence_digest']);return self.emit(copy.deepcopy(self.raw(d['id'])),rid,'suppression_reported',signature,self.raw(d['id'])['revision'])
    else:raise CRMError('EMAIL_CAMPAIGN_STATE_REQUIRED',409)
   return self.emit(d,rid,op,signature,body['expected_revision'])
 def proof(self,d,r):return hmac.new(self.secret('COMMERCIAL_EMAIL_LINK_KEYS'),(self.key()+':'+d['id']+':'+r['contact_id']+':'+r['email']).encode(),hashlib.sha256).hexdigest()
 def preview(self,ref,contact_id):
  self.authority();d=self.get(ref);r=next((r for r in d['recipients'] if r['contact_id']==contact_id),None)
  if not r:raise CRMError('EMAIL_RECIPIENT_NOT_FOUND',404)
  return self.render(d,r,preview=True)
 def render(self,d,r,preview=False):
  p=self.policy();company=p['sender_name'];substitute=lambda s:s.replace('{{name}}',r['name']).replace('{{company}}',company)
  url=p['public_base_url'].rstrip('/')+('/api/v1/mi-negocio/comercial/unified/' if SYSTEM=='erp-tur' else '/api/v1/commercial-unified/')+'email-unsubscribe/'+d['id']+'/'+r['contact_id']+'/'+('PREVIEW_NOT_A_LINK' if preview else self.proof(d,r))+'/'
  subject=substitute(d['subject'])
  if any(ord(c)<32 for c in subject):raise CRMError('EMAIL_HEADER_CONTROL_REJECTED')
  plain=substitute(d['body_text'])+'\n\n'+company+'\n'+p['postal_address']+'\nCancelar comunicaciones: '+url
  body='<!doctype html><html lang="es"><meta charset="utf-8"><body style="background:#11304b;color:white;font:16px sans-serif;padding:24px"><h1>'+html.escape(company if d['template']=='LETTER' else subject)+'</h1>'+''.join('<p>'+html.escape(line)+'</p>' for line in substitute(d['body_text']).splitlines())+'<hr><p>'+html.escape(p['postal_address'])+'</p><a style="color:#96d7ff" href="'+html.escape(url,quote=True)+'">Cancelar comunicaciones</a></body></html>'
  return {'subject':subject,'text':plain,'html':body,'unsubscribe_url':url,'preview':preview,'mail_sent':False}
 def unsubscribe(self,ref,contact,proof):
  d=self.raw(ref);r=next((r for r in d.get('recipients',[]) if r['contact_id']==contact),None)
  if not r or not isinstance(proof,str) or not hmac.compare_digest(self.proof(d,r),proof):raise CRMError('EMAIL_UNSUBSCRIBE_NOT_FOUND',404)
  with self.store.transaction():self.store.lock();self.suppress(r['email'],'UNSUBSCRIBED')
  return {'unsubscribed':True,'pending_blocked':True,'already_dispatched_cannot_be_recalled':True}
 def claim(self,ref,contact):
  self.authority()
  if os.environ.get('COMMERCIAL_EMAIL_WORKER_ENABLED')!='1':raise CRMError('EMAIL_WORKER_DISABLED',503)
  with self.store.transaction():
   self.authority();self.store.lock();d=copy.deepcopy(self.get(ref));p=self.policy()
   if d['kind']!='CAMPAIGN' or d['status']!='SCHEDULED' or d['creator_ref']!=self.actor or moment(d['scheduled_at'])>self.clock() or digest(p)!=d['sender_policy_digest'] or not p['allow_dispatch']:raise CRMError('EMAIL_NOT_DISPATCHABLE',409)
   r=next((r for r in d['recipients'] if r['contact_id']==contact),None)
   if not r or r['status']!='PENDING':raise CRMError('EMAIL_RECIPIENT_NOT_PENDING',409)
   if self.suppressed(r['email']) or not self.eligible(contact,r['email']):r['status']='SUPPRESSED';d['status']='PROCESSED' if all(x['status'] not in ('PENDING','DISPATCHING') for x in d['recipients']) else d['status'];self.emit(d,str(uuid.uuid4()),'skip_ineligible','worker',d['revision']);return None
   if digest(self.crm.get(contact).get('consents',{}).get('EMAIL:MARKETING',{}))!=r['consent_digest']:r['status']='CONSENT_CHANGED';self.emit(d,str(uuid.uuid4()),'skip_changed_consent','worker',d['revision']);return None
   today=self.clock().date();count=sum(1 for c in self.records() if c['kind']=='CAMPAIGN' for row in c['recipients'] if row.get('claimed_at') and moment(row['claimed_at']).date()==today)
   if count>=p['daily_limit']:raise CRMError('EMAIL_DAILY_QUOTA',429)
   r['status']='DISPATCHING';r['claimed_at']=self.clock().isoformat();r['attempts']=1;r['message_id']='<'+d['id']+'.'+hashlib.sha256(contact.encode()).hexdigest()[:16]+'@'+p['sender_email'].split('@')[1]+'>';token=secrets.token_hex(32);r['claim_hash']=hashlib.sha256(token.encode()).hexdigest();self.emit(d,str(uuid.uuid4()),'dispatch_claim','worker',d['revision']);return copy.deepcopy(d),copy.deepcopy(r),token,self.render(d,r)
 def finish(self,ref,contact,token,status):
  self.authority()
  if status not in ('ACCEPTED','REJECTED','UNCERTAIN','SUPPRESSED'):raise CRMError('EMAIL_INVALID_TRANSPORT_STATUS')
  with self.store.transaction():
   self.authority();self.store.lock();d=copy.deepcopy(self.get(ref));r=next((r for r in d['recipients'] if r['contact_id']==contact),None)
   if not r or r['status']!='DISPATCHING' or not hmac.compare_digest(r['claim_hash'],hashlib.sha256(token.encode()).hexdigest()):raise CRMError('EMAIL_DISPATCH_REVIEW_REQUIRED',409)
   r['status']=status;r['accepted_at']=self.clock().isoformat() if status=='ACCEPTED' else None;r['claim_hash']=None;r['error_code']='TRANSPORT_OUTCOME_UNKNOWN_NO_AUTO_RETRY' if status=='UNCERTAIN' else None
   if all(x['status']!='PENDING' and x['status']!='DISPATCHING' for x in d['recipients']):d['status']='PROCESSED'
   return self.emit(d,str(uuid.uuid4()),'transport_result','worker',d['revision'])
 def provider_receipt(self,body,signature):
  if not isinstance(body,dict) or set(body)!={'event_id','campaign_id','contact_id','message_id','status','occurred_at'} or body['status'] not in ('SENT','DELIVERED','BOUNCED','COMPLAINT'):raise CRMError('EMAIL_INVALID_PROVIDER_EVENT')
  expected=hmac.new(self.secret('COMMERCIAL_EMAIL_RECEIPT_KEYS'),digest(body).encode(),hashlib.sha256).hexdigest()
  if not isinstance(signature,str) or not hmac.compare_digest(expected,signature):raise CRMError('EMAIL_PROVIDER_SIGNATURE_REJECTED',401)
  rid=uuid_ref(body['event_id']);stamp=moment(body['occurred_at']);fingerprint=digest(body)
  with self.store.transaction():
   self.store.lock();prior=self.store.event(rid)
   if prior:
    if prior.get('scope')!=self.store.scope or prior.get('provider_ref')!=getattr(self.store,'provider',None) or prior.get('fingerprint')!=fingerprint:raise CRMError('EMAIL_PROVIDER_EVENT_CONFLICT',409)
    self.raw(prior['item_id']);return {'recorded':True,'replayed':True}
   d=copy.deepcopy(self.raw(uuid_ref(body['campaign_id'])));r=next((r for r in d.get('recipients',[]) if r['contact_id']==body['contact_id']),None)
   if not r or r['message_id']!=body['message_id'] or not r.get('claimed_at') or not moment(r['claimed_at'])<=stamp<=self.clock()+timedelta(minutes=5):raise CRMError('EMAIL_PROVIDER_EVENT_MISMATCH',409)
   if r['status'] not in ('ACCEPTED','SENT','DELIVERED') or r['status']=='DELIVERED' and body['status'] in ('SENT','BOUNCED'):raise CRMError('EMAIL_PROVIDER_ORDER_REVIEW_REQUIRED',409)
   if body['status']=='SENT':r['sent_at']=stamp.isoformat()
   elif body['status']=='DELIVERED':r['delivered_at']=stamp.isoformat()
   r['status']=body['status'];r['receipt_source']='SIGNED_ADAPTER_REPORT';r['provider_authenticity_qualified']=False
   self.emit(d,rid,'provider_report',fingerprint,d['revision'])
   if body['status'] in ('BOUNCED','COMPLAINT'):self.suppress(r['email'],body['status'],fingerprint)
   return {'recorded':True,'provider_report_only':True,'provider_authenticity_qualified':False}
def email(value):
 if not isinstance(value,str) or len(value)>254 or not re.fullmatch(r'[A-Za-z0-9_.+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+',value):raise CRMError('EMAIL_ADDRESS_REQUIRED')
 return value.lower()
def validate_template(value):
 stripped=value.replace('{{name}}','').replace('{{company}}','')
 if '{{' in stripped or '}}' in stripped:raise CRMError('EMAIL_TEMPLATE_VARIABLE_NOT_ALLOWED')

def contact_ref(value):
 if SYSTEM!='sga-cd' and isinstance(value,str) and re.fullmatch(r'customer:[1-9][0-9]{0,17}',value):return value
 return uuid_ref(value)
