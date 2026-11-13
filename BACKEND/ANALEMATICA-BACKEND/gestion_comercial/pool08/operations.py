"""Private, bounded operational evidence. Never calls providers or writes a ledger."""
import importlib,re,time,logging
from collections import Counter
from itertools import islice
from datetime import datetime,timezone
from .crm import CRMError,digest
from .contract import SYSTEM
from .opportunities import uuid_ref
DOMAINS={'opportunities':'opportunity_store','pricing':'pricing_store','quotations':'quotation_store','sales':'sales_store','landings':'landing_store','library':'library_store','generation':'generation_store','email':'email_campaign_store','mobile':'mobile_message_store','publishing':'publishing_store','inbox':'inbox_store','ads':'ads_store','army':'army_store','analytics':'analytics_store','payments':'payment_store','capture':'capture_store'}
class Operations:
 def __init__(self,crm):self.crm=crm
 def authority(self):
  a=self.crm.authorize()
  if not a.principal['is_manager']:raise CRMError('OPERATIONS_MANAGER_REQUIRED',403)
  return a
 def store(self,domain):
  if domain not in DOMAINS:raise CRMError('OPERATIONS_DOMAIN_NOT_ALLOWED',400)
  return importlib.import_module(__package__+'.'+DOMAINS[domain]).Store(self.crm.store)
 def checked(self,store,ref):
  # A record and its events may straddle a legitimate committed revision.
  # Retry only when the checked document changed; a stable corrupt chain fails.
  ref=uuid_ref(ref)
  for attempt in range(2):
   d=store.get(ref)
   if not d or d.get('creator_ref',self.crm.actor)!=self.crm.actor:raise CRMError('OPERATIONS_RECORD_NOT_FOUND',404)
   if 'permission_digest' in d and d['permission_digest']!=digest(self.authority().session()['capability_permissions']):raise CRMError('OPERATIONS_PERMISSIONS_CHANGED',403)
   events=list(islice(store.events(ref),1001));previous='0'*64
   if len(events)>1000:raise CRMError('OPERATIONS_TRACE_LIMIT',503)
   latest=store.get(ref)
   if latest is None or digest(latest)!=digest(d):continue
   for e in events:
    if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('OPERATIONS_EVENT_INTEGRITY_REQUIRED',503)
    previous=e['event_digest']
   if not events or len(events)!=d['revision'] or previous!=d.get('last_event_digest') or events[-1].get('result_digest')!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('OPERATIONS_STATE_INTEGRITY_REQUIRED',503)
   return d,events
  raise CRMError('OPERATIONS_CHANGED_RETRY',409)
 def trace(self,domain,ref):
  self.authority();d,events=self.checked(self.store(domain),ref);self.authority()
  return {'system':SYSTEM,'domain':domain,'record_id':ref,'scope':self.crm.store.scope,'provider_ref':getattr(self.crm.store,'provider',None),'revision':d['revision'],'state':d.get('status',d.get('stage')),'state_digest':digest(d),'events':[{'id':e['id'],'operation':e['operation'],'created_at':e['created_at'],'event_digest':e['event_digest'],'previous_event_digest':e['previous_event_digest'],'result_digest':e['result_digest']} for e in events],'chain_verified':True,'source_authenticity_or_provider_acceptance':False,'ledger_or_provider_action':False}
 def health(self):
  self.authority();start=time.perf_counter();rows=[]
  for domain in DOMAINS:
   self.authority();started=time.perf_counter()
   try:
    store=self.store(domain);sample,more=store.list('','',0,20)
    sample=[self.checked(store,d['id'])[0] for d in sample]
    row={'domain':domain,'state':'AVAILABLE','sample_count':len(sample),'sample_limit':20,'more_records':more,'counts_by_state':dict(Counter(d.get('status',d.get('stage','UNKNOWN')) for d in sample)),'sample_digest':digest(sample),'is_full_population':not more}
   except Exception as error:
    code=str(error) if isinstance(error,CRMError) and re.fullmatch('[A-Z0-9_]{1,100}',str(error)) else 'OPERATIONS_SOURCE_REVIEW_REQUIRED'
    row={'domain':domain,'state':'UNAVAILABLE','reason':code,'sample_count':None,'is_full_population':False}
   row['read_ms']=round((time.perf_counter()-started)*1000,3);rows.append(row)
  self.authority();elapsed=round((time.perf_counter()-start)*1000,3);state='AVAILABLE' if all(r['state']=='AVAILABLE' for r in rows) else 'PARTIAL'
  logging.getLogger(__name__).info('commercial_operational_probe system=%s state=%s duration_ms=%s unavailable=%s',SYSTEM,state,elapsed,sum(r['state']!='AVAILABLE' for r in rows))
  return {'system':SYSTEM,'scope':self.crm.store.scope,'actor_ref':self.crm.actor,'provider_ref':getattr(self.crm.store,'provider',None),'observed_at':datetime.now(timezone.utc).isoformat(),'state':state,'sources':rows,'duration_ms':elapsed,'provider_calls':0,'ledger_writes':0,'hardware_or_production_qualified':False,'latency_targets':{'ui_seconds':1.2,'read_seconds':3,'media_seconds':60,'qualified':False},'note':'Measured bounded source reads on this host; not HTTP load, media generation, durability certification or production acceptance.'}
