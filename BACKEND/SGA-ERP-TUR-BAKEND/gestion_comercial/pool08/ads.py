"""Owned paid-media governance. Planning reservations are not financial holds.

This increment reviews local campaigns and experiment plans. It does not create
provider ad sets/creatives or enable spending. Live execution stays fail-closed.
"""
import copy,os,json,uuid,re
from datetime import datetime,timezone
from .crm import CRMError,text,digest as base_digest
from .opportunities import uuid_ref
from .contract import SYSTEM
MAX_RECORDS=500
PLATFORMS=('META','TIKTOK','GOOGLE_YOUTUBE')
def digest(value):
 try:return base_digest(value)
 except UnicodeError:raise CRMError('ADS_INVALID_TEXT') from None
class Ads:
 def __init__(self,store,crm,clock=None):self.store,self.crm=store,crm;self.actor=crm.actor;self.clock=clock or (lambda:datetime.now(timezone.utc))
 def authority(self):
  access=self.crm.authorize()
  if not access.principal['is_manager'] or not access.session()['capability_permissions'].get('ads.campaign.manage'):raise CRMError('ADS_PERMISSION_REQUIRED',403)
 def key(self):return SYSTEM+':'+self.store.scope+':'+(getattr(self.store,'provider',None) or '-')
 def policy(self):
  try:
   p=json.loads(os.environ.get('COMMERCIAL_ADS_LIMITS','{}'))[SYSTEM+':'+self.store.scope]
   if not isinstance(p,dict) or set(p)!={'version','currency','max_reserved_minor','max_daily_minor','support_digest'} or p['currency']!='COP':raise ValueError()
   text(p['version'],80)
   for name in ('max_reserved_minor','max_daily_minor'):
    if type(p[name])!=int or not 1<=p[name]<=10**12:raise ValueError()
   if not re.fullmatch('[a-f0-9]{64}',str(p['support_digest'])):raise ValueError()
   return copy.deepcopy(p)
  except (KeyError,ValueError,TypeError,AttributeError):raise CRMError('ADS_COMPANY_LIMITS_REQUIRED',503) from None
 def profile(self,account,platform):
  try:
   p=json.loads(os.environ.get('COMMERCIAL_ADS_ACCOUNTS','{}'))[self.key()][account]
   if not isinstance(p,dict) or set(p)!={'version','platform','account_id','currency','ownership_support_digest'} or p['platform']!=platform or p['currency']!='COP':raise ValueError()
   text(p['version'],80)
   if not re.fullmatch('[A-Za-z0-9_-]{1,100}',str(p['account_id'])) or not re.fullmatch('[a-f0-9]{64}',str(p['ownership_support_digest'])):raise ValueError()
   return copy.deepcopy(p)
  except (KeyError,ValueError,TypeError,AttributeError):raise CRMError('ADS_ACCOUNT_PROFILE_REQUIRED',503) from None
 def raw(self,ref):
  uuid_ref(ref);d=self.store.get(ref)
  if not d:raise CRMError('ADS_RECORD_NOT_FOUND',404)
  previous='0'*64;events=list(self.store.events(ref))
  for e in events:
   if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('ADS_HISTORY_REVIEW_REQUIRED',503)
   previous=e['event_digest']
  if not events or len(events)!=d['revision'] or previous!=d['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('ADS_INTEGRITY_REVIEW_REQUIRED',503)
  return d
 def get(self,ref):self.authority();d=self.raw(ref);return d
 def records(self):
  rows=list(self.store.all_jobs())
  if len(rows)>MAX_RECORDS:raise CRMError('ADS_RECORD_LIMIT',409)
  return [self.raw(r['id']) for r in rows]
 def emit(self,d,rid,op,signature,expected):
  d['revision']=expected+1;d['updated_at']=self.clock().isoformat();receipt={'request_id':rid,'job_id':d['id'],'status':d['status'],'revision':d['revision'],'network_call_by_command':op.startswith('worker_')}
  e={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':d['id'],'operation':op,'fingerprint':signature,'previous_event_digest':d.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in d.items() if k!='last_event_digest'}),'receipt':receipt,'created_at':self.clock().isoformat()};e['event_digest']=digest(e);d['last_event_digest']=e['event_digest'];self.store.save(d,expected);self.store.append(e);return receipt
 def history(self,ref):
  self.get(ref);return {'events':list(self.store.events(ref)),'history_verified':True}
 def receipt(self,rid):
  self.authority();uuid_ref(rid);e=self.store.event(rid)
  if not e or e.get('scope')!=self.store.scope or e.get('provider_ref')!=getattr(self.store,'provider',None) or e.get('actor')!=self.actor:raise CRMError('ADS_RECEIPT_NOT_FOUND',404)
  self.raw(e['item_id']);return e['receipt']|{'previous_receipt_only':True}
 def list(self):
  self.authority();p=self.policy();return {'campaigns':[{k:d[k] for k in ('id','title','platform','status','revision','total_budget_minor','daily_budget_minor','currency','reserved')} for d in self.records()],'company_planned_reserved_minor':self.company_reserved(),'limits':p,'remote_campaigns_created':False,'spending_enabled':False,'execution_qualified':False}
 def company_reserved(self,field='total_budget_minor'):
  if field not in ('total_budget_minor','daily_budget_minor'):raise CRMError('ADS_BUDGET_FIELD_INVALID')
  total=0
  for d in self.store.company_jobs():
   previous='0'*64;events=list(self.store.events(d['id']))
   for e in events:
    if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('ADS_COMPANY_HISTORY_REVIEW_REQUIRED',503)
    previous=e['event_digest']
   if not events or len(events)!=d['revision'] or previous!=d['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('ADS_COMPANY_INTEGRITY_REVIEW_REQUIRED',503)
   if d['reserved']:total+=d[field]
  return total
 def assets(self,variants,platform):
  if not isinstance(variants,list) or len(variants)!=2:raise CRMError('ADS_TWO_VARIANTS_REQUIRED')
  from .library_api import service
  from .publishing_api import service as publishing
  assets=[];weights=[]
  for i,v in enumerate(variants):
   if not isinstance(v,dict) or set(v)!={'label','headline','weight','media_ref'} or v['label']!=('A' if i==0 else 'B') or type(v['weight'])!=int or not 20<=v['weight']<=80:raise CRMError('ADS_VARIANT_INVALID')
   text(v['headline'],100);ref=v['media_ref']
   if not isinstance(ref,dict) or set(ref)!={'item_id','version','sha256'}:raise CRMError('ADS_MEDIA_REQUIRED')
   item=service(self.crm).get(ref['item_id']);version=next((x for x in item['versions'] if x['number']==ref['version']),None)
   if not version:raise CRMError('ADS_MEDIA_REQUIRED')
   kind=version['media']['kind']
   if platform!='META' and kind!='VIDEO':raise CRMError('ADS_PLATFORM_REQUIRES_VIDEO')
   profile='FACEBOOK_PHOTO' if kind=='IMAGE' else 'YOUTUBE_VIDEO';assets.append(publishing(self.crm).asset(ref,profile));weights.append(v['weight'])
  if sum(weights)!=100:raise CRMError('ADS_SPLIT_MUST_TOTAL_100')
  return assets
 def allocations(self,d):
  amounts=[]
  for variant in d['variants']:
   total=d['total_budget_minor']*variant['weight'];daily=d['daily_budget_minor']*variant['weight']
   if total%100 or daily%100:raise CRMError('ADS_FRACTIONAL_MINOR_UNIT_REJECTED')
   amounts.append({'variant':variant['label'],'planned_total_minor':total//100,'planned_daily_minor':daily//100})
  return amounts
 def command(self,body):
  self.authority()
  if not isinstance(body,dict) or set(body)!={'request_id','operation','job_id','expected_revision','data'} or type(body['expected_revision'])!=int or not 0<=body['expected_revision']<1000 or not isinstance(body['data'],dict):raise CRMError('ADS_INVALID_COMMAND')
  rid=uuid_ref(body['request_id']);op=body['operation'];data=body['data'];fingerprint=digest({'key':self.key(),'actor':self.actor,'body':body})
  with self.store.transaction():
   self.store.lock();self.authority();prior=self.store.event(rid)
   if prior:
    self.receipt(rid)
    if prior['fingerprint']!=fingerprint:raise CRMError('ADS_REQUEST_CONFLICT',409)
    return prior['receipt']|{'replayed':True}
   if op=='create':
    fields={'title','platform','account_ref','currency','total_budget_minor','daily_budget_minor','duration_days','variants'}
    if body['job_id'] is not None or body['expected_revision']!=0 or set(data)!=fields or not isinstance(data['platform'],str) or data['platform'] not in PLATFORMS or data['currency']!='COP':raise CRMError('ADS_INVALID_DRAFT')
    for k in ('total_budget_minor','daily_budget_minor','duration_days'):
     if type(data[k])!=int or data[k]<=0:raise CRMError('ADS_EXACT_POSITIVE_INTEGER_REQUIRED')
    if data['duration_days']>30 or not data['daily_budget_minor']<=data['total_budget_minor']<=data['daily_budget_minor']*data['duration_days'] or data['total_budget_minor']>10**12:raise CRMError('ADS_BUDGET_RANGE')
    if len(self.records())>=200:raise CRMError('ADS_CAMPAIGN_LIMIT',409)
    ref=str(uuid.uuid4());d={'id':ref,'code':ref,'kind':'CAMPAIGN','title':text(data['title'],150),'platform':data['platform'],'account_ref':text(data['account_ref'],100),'currency':'COP','total_budget_minor':data['total_budget_minor'],'daily_budget_minor':data['daily_budget_minor'],'duration_days':data['duration_days'],'variants':copy.deepcopy(data['variants']),'creator_ref':self.actor,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'revision':0,'status':'DRAFT','reserved':False,'created_at':self.clock().isoformat(),'review':None,'authorization':None,'observations':[],'proposal':None,'control_brief':None,'remote_campaign_id':None,'real_spend_minor':None,'remote_state':'NOT_CREATED','execution_qualified':False}
    d['profile_digest']=digest(self.profile(d['account_ref'],d['platform']));d['policy_digest']=digest(self.policy());d['asset_snapshots']=self.assets(d['variants'],d['platform']);d['allocations']=self.allocations(d)
   else:
    d=copy.deepcopy(self.get(uuid_ref(body['job_id'])))
    if d['revision']!=body['expected_revision']:raise CRMError('ADS_REVISION_CONFLICT',409)
    if d['creator_ref']!=self.actor:raise CRMError('ADS_SAME_ADMIN_REQUIRED',403)
    if op=='review' and d['status']=='DRAFT' and data=={'confirmed_creatives':True,'confirmed_budget':True} and all(type(v)==bool for v in data.values()):
     if self.assets(d['variants'],d['platform'])!=d['asset_snapshots']:raise CRMError('ADS_MEDIA_CHANGED',409)
     d['review']={'actor':self.actor,'request_id':rid};d['status']='REVIEWED'
    elif op=='approve_plan' and d['status']=='REVIEWED' and set(data)=={'confirmed_impact','maximum_minor'} and data['confirmed_impact'] is True and type(data['maximum_minor'])==int and data['maximum_minor']>=d['total_budget_minor']:
     p=self.policy()
     if digest(p)!=d['policy_digest'] or digest(self.profile(d['account_ref'],d['platform']))!=d['profile_digest'] or self.assets(d['variants'],d['platform'])!=d['asset_snapshots']:raise CRMError('ADS_REVIEW_CHANGED',409)
     if self.company_reserved()+d['total_budget_minor']>p['max_reserved_minor'] or self.company_reserved('daily_budget_minor')+d['daily_budget_minor']>p['max_daily_minor']:raise CRMError('ADS_COMPANY_LIMIT_EXCEEDED',409)
     d['reserved']=True;d['status']='LOCAL_APPROVED';d['authorization']={'actor':self.actor,'request_id':rid,'maximum_minor':data['maximum_minor']}
    elif op=='prepare_control' and not data and d['status']=='LOCAL_APPROVED':
     if digest(self.policy())!=d['policy_digest'] or digest(self.profile(d['account_ref'],d['platform']))!=d['profile_digest'] or self.assets(d['variants'],d['platform'])!=d['asset_snapshots']:raise CRMError('ADS_REVIEW_CHANGED',409)
     d['control_brief']=self.control_brief(d)
    elif op=='cancel' and not data and d['status'] in ('DRAFT','REVIEWED','LOCAL_APPROVED'):d['status']='CANCELLED';d['reserved']=False;d['control_brief']=None
    elif op=='observe' and d['status']=='LOCAL_APPROVED' and set(data)=={'source','support_digest','variants'} and data['source']=='MANUAL_DECLARED' and re.fullmatch('[a-f0-9]{64}',str(data['support_digest'])):
     rows=data['variants']
     if not isinstance(rows,list) or len(rows)!=2 or len(d['observations'])>=20:raise CRMError('ADS_OBSERVATION_LIMIT')
     for i,row in enumerate(rows):
      if not isinstance(row,dict) or set(row)!={'label','impressions','clicks','cost_minor'} or row['label']!=('A' if i==0 else 'B') or any(type(row[k])!=int or not 0<=row[k]<=10**12 for k in ('impressions','clicks','cost_minor')) or row['clicks']>row['impressions']:raise CRMError('ADS_OBSERVATION_INVALID')
     observation=copy.deepcopy(data)|{'received_at':self.clock().isoformat(),'authenticity_verified':False};d['control_brief']=None;d['observations'].append(observation);d['proposal']=self.propose(d,observation)
    else:raise CRMError('ADS_STATE_REQUIRED',409)
   return self.emit(d,rid,op,fingerprint,body['expected_revision'])
 def propose(self,d,observation):
  a,b=observation['variants'];proposal={'state':'INSUFFICIENT_REVIEWED_DATA','automatically_applied':False,'source_authenticity_verified':False,'requires_new_review':True,'weights':[v['weight'] for v in d['variants']]}
  if min(a['clicks'],b['clicks'])<100 or min(a['cost_minor'],b['cost_minor'])<=0:return proposal
  if a['cost_minor']*b['clicks']*100>b['cost_minor']*a['clicks']*125:direction=-10
  elif b['cost_minor']*a['clicks']*100>a['cost_minor']*b['clicks']*125:direction=10
  else:return proposal|{'state':'NO_SIGNIFICANT_DECLARED_CPC_DIFFERENCE'}
  weight=max(20,min(80,d['variants'][0]['weight']+direction));return proposal|{'state':'PROPOSAL_ONLY','weights':[weight,100-weight],'basis':'declared CPC, >25% difference; not causal inference or ROI guarantee'}
 def control_brief(self,d):
  from pathlib import Path
  contract=json.loads(Path(__file__).with_name('ads-control-contract.json').read_text());target=contract['platforms'][d['platform']]
  snapshot={k:d[k] for k in ('id','platform','account_ref','total_budget_minor','daily_budget_minor','variants','authorization','profile_digest','policy_digest')}
  brief={'engine':'Open Duet + agent-desktop','mode':'plan','operational_general':'Jarvi','conversational_general':'Neko','agent_optimizer':'SOUP','source':{'system':SYSTEM,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'plan_id':d['id'],'source_revision':d['revision']+1,'approved_plan_digest':digest(snapshot)},'workflow_id':target['workflow'],'platform':target['platform'],'policy_version':contract['policy_version'],'policy_reference_sha256':contract['reference_sha256'],'suggested_read_intents':[{'operation':'browser_open','arguments':{'url':target['url']}},{'operation':'browser_snapshot','arguments':{}}],'required_independent_authorizations':contract['authorizations'],'device_binding_required':True,'account_identity_must_be_verified_by_operator':True,'mutations_require_fresh_observation_refs':True,'execution_grant':None,'spending_authorization':False,'submitted_to_engine':False}
  return brief|{'brief_digest':digest(brief)}
 def execute(self,ref):
  self.get(ref)
  # A reviewed local reservation is never a provider's spend authorization.
  raise CRMError('ADS_PROVIDER_EXECUTION_NOT_QUALIFIED',503)
