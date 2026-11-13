"""Reproducible commercial reports. Null means unavailable, never silently zero."""
import json,os,copy,uuid,re
from datetime import datetime,date,timedelta,timezone
from decimal import Decimal,Context,localcontext
from collections import Counter,defaultdict
from .crm import CRMError,digest as base_digest,text
from .contract import SYSTEM
from .opportunities import uuid_ref
from .analytics_forecast import forecast,money
MAX_RECORDS=500
def digest(value):
 try:return base_digest(value)
 except UnicodeError:raise CRMError('ANALYTICS_INVALID_TEXT') from None
class Analytics:
 def __init__(self,store,crm,clock=None,remote_reader=None):self.remote_reader=remote_reader;self.store,self.crm=store,crm;self.actor=crm.actor;self.clock=clock or (lambda:datetime.now(timezone.utc))
 def authority(self):
  access=self.crm.authorize()
  if not access.principal['is_manager']:raise CRMError('ANALYTICS_MANAGER_REQUIRED',403)
  return access
 def raw(self,ref):
  uuid_ref(ref);d=self.store.get(ref)
  if not d:raise CRMError('ANALYTICS_RECORD_NOT_FOUND',404)
  previous='0'*64;events=list(self.store.events(ref))
  for e in events:
   if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('ANALYTICS_HISTORY_REVIEW_REQUIRED',503)
   previous=e['event_digest']
  if not events or len(events)!=d['revision'] or previous!=d['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('ANALYTICS_INTEGRITY_REVIEW_REQUIRED',503)
  return d
 def records(self):
  rows=list(self.store.all_jobs())
  if len(rows)>MAX_RECORDS:raise CRMError('ANALYTICS_RECORD_LIMIT',409)
  return [self.raw(r['id']) for r in rows]
 def emit(self,d,rid,op,signature,expected):
  d['revision']=expected+1;d['updated_at']=self.clock().isoformat();receipt={'request_id':rid,'job_id':d['id'],'status':d['status'],'revision':d['revision'],'provider_reads_requested':d['query']['provider_reads']}
  e={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':d['id'],'operation':op,'fingerprint':signature,'previous_event_digest':d.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in d.items() if k!='last_event_digest'}),'receipt':receipt,'created_at':self.clock().isoformat()};e['event_digest']=digest(e);d['last_event_digest']=e['event_digest'];self.store.save(d,expected);self.store.append(e);return receipt
 def history(self,ref):
  self.get(ref);return {'events':list(self.store.events(ref)),'history_verified':True}
 def receipt(self,rid):
  self.authority();uuid_ref(rid);e=self.store.event(rid)
  if not e or e.get('scope')!=self.store.scope or e.get('provider_ref')!=getattr(self.store,'provider',None) or e.get('actor')!=self.actor:raise CRMError('ANALYTICS_RECEIPT_NOT_FOUND',404)
  self.get(e['item_id']);return e['receipt']|{'previous_receipt_only':True}
 def list(self):
  self.authority();return {'reports':[{k:d[k] for k in ('id','title','status','revision','created_at')} for d in self.records() if d['creator_ref']==self.actor],'live_provider_reads_enabled':os.environ.get('COMMERCIAL_ANALYTICS_PROVIDER_READ_ENABLED')=='1','real_provider_qualified':False}
 def get(self,ref):
  access=self.authority();d=self.raw(ref)
  if d['creator_ref']!=self.actor or d['permission_digest']!=digest(access.session()['capability_permissions']):raise CRMError('ANALYTICS_PERMISSIONS_CHANGED',403)
  return d
 def collect(self,since,until,provider_reads=False,client_factory=None):
  self.authority();from . import analytics_sources as sources
  source_meta={};warnings=[]
  def read(name,operation):
   self.authority()
   try:
    value=operation();source_meta[name]={'state':'AVAILABLE','digest':digest(value),'observed_at':self.clock().isoformat(),'coverage':'OWNED_MODULE_ONLY'};return value
   except Exception as error:
    code=str(error) if isinstance(error,CRMError) and re.fullmatch('[A-Z0-9_]{1,100}',str(error)) else 'SOURCE_REQUIRES_REVIEW';source_meta[name]={'state':'UNAVAILABLE','reason':code,'observed_at':self.clock().isoformat()};warnings.append(name+':'+code);return None
  people=read('crm',lambda:sources.contacts(self.crm))
  pipeline=read('opportunities',lambda:sources.opportunities(self.crm))
  from .sales_store import Store as SaleStore
  sales=read('sales',lambda:sources.documents(SaleStore(self.crm.store)))
  economics=read('ledger',lambda:sources.income(self.crm,sales,self.remote_reader)) if sales is not None else None
  if sales is None:source_meta['ledger']={'state':'UNAVAILABLE','reason':'SALES_SOURCE_UNAVAILABLE'}
  attribution=read('attribution',lambda:sources.attribution(self.crm,people,economics,since,until)) if people is not None else None
  from .analytics_costs import collect as costs
  spending=read('providers',lambda:costs(self.crm,since,until,client_factory)) if provider_reads else None
  if not provider_reads:source_meta['providers']={'state':'NOT_REQUESTED','reason':'NO_ESTIMATED_BUDGET_SUBSTITUTION'}
  current_funnel=None if people is None else {'contacts':len(people),'by_status':dict(Counter(p['status'] for p in people)),'crm_converted_contacts':sum(p['status']=='CUSTOMER' for p in people),'time_basis':'CURRENT_SNAPSHOT_NOT_HISTORICAL_FUNNEL','a_customer_is_not_a_posted_sale':True}
  period=None;prediction={'state':'SOURCE_UNAVAILABLE','predictions':[],'calibrated_for_production':False};cac={'value':None,'state':'COST_OR_LEDGER_SOURCE_MISSING'}
  with localcontext(Context(prec=50)):
   if economics is not None:
    all_rows=economics['rows'];rows=[r for r in all_rows if since<=r['date']<=until];total=sum((money(r['amount']) for r in rows),Decimal('0'));sales_count=sum(r['kind']=='SALE' for r in rows);reversals=sum(r['kind']=='REVERSAL' for r in rows);buyers={r['contact_id'] for r in rows if r['kind']=='SALE'};first={}
    for r in all_rows:
     if r['kind']=='SALE':first[r['contact_id']]=min(first.get(r['contact_id'],r['date']),r['date'])
    new=sum(since<=day<=until for day in first.values());period={'recognized_sales':sales_count,'recognized_reversals':reversals,'net_revenue_cop':format(total,'.2f'),'customers':len(buyers),'new_to_module_customers':new,'observed_revenue_per_module_customer_cop':format((total/len(buyers)).quantize(Decimal('.01')),'.2f') if buyers else None,'scope':economics['scope'],'ledger_proof_digest':digest(economics['proof']),'scope_is_entire_company':False}
    daily=defaultdict(lambda:Decimal('0'))
    for r in rows:daily[r['date']]+=money(r['amount'])
    series=[];day=date.fromisoformat(since);last=date.fromisoformat(until)
    while day<=last:series.append({'date':day.isoformat(),'value':format(daily[day.isoformat()],'.2f')});day+=timedelta(days=1)
    prediction=forecast(series);prediction['series_digest']=digest(series);prediction['scope']=economics['scope'];prediction['explicit_zero_days_from_complete_module_source']=True
    if spending is not None:
     cost=sum((Decimal(r['cost_cop']) for r in spending['rows']),Decimal('0'));cac={'value':format((cost/new).quantize(Decimal('.01')),'.2f') if new and cost>=0 else None,'cost_cop_exact':format(cost,'f'),'new_to_module_customers':new,'state':'LIMITED_SCOPE_RATIO' if new and cost>=0 else 'NO_NEW_CUSTOMERS_OR_COST_CREDIT_REVIEW','scope':'CONFIGURED_ACCOUNT_REPORTED_COST_PER_NEW_MODULE_CUSTOMER','is_global_or_causal_CAC':False,'real_provider_qualified':False}
  # Lifetime margin/retention cannot be inferred from sales counts or one period's ARPU.
  from .analytics_ltv import estimate as lifetime
  ltv=read('ltv_policy',lambda:lifetime(self.crm,economics,since,until,self.clock()))
  if ltv is None:ltv={'value':None,'state':'LTV_POLICY_UNAVAILABLE','calibrated_for_production':False}
  return {'cut':{'since':since,'until':until,'economic_dates':'RECORDED_LEDGER_ENTRY_DATE','observed_at':self.clock().isoformat(),'time_zone':'America/Bogota','historical_crm_states_reconstructed':False},'sources':source_meta,'current_funnel':current_funnel,'current_opportunity_funnel':None if pipeline is None else {'opportunities':len(pipeline),'by_stage':dict(Counter(d['stage'] for d in pipeline)),'won_is_not_recognized_revenue':True,'time_basis':'CURRENT_SNAPSHOT_NOT_HISTORICAL_TRANSITION_RATES'},'module_sales_states':dict(Counter(d['status'] for d in sales)) if sales is not None else None,'period_economics':period,'attribution':attribution,'reported_provider_costs':spending,'CAC':cac,'LTV':ltv,'forecast':prediction,'warnings':warnings,'state':'PARTIAL' if warnings else 'SOURCE_SNAPSHOT','fiscal_or_bank_action_executed':False}
 def command(self,body,client_factory=None):
  self.authority()
  if isinstance(body,dict) and body.get('operation')=='recover':return self.recover(body)
  if not isinstance(body,dict) or set(body)!={'request_id','operation','job_id','expected_revision','data'} or body['operation']!='build' or body['job_id'] is not None or body['expected_revision']!=0 or type(body['expected_revision'])!=int or not isinstance(body['data'],dict) or set(body['data'])!={'since','until','provider_reads','confirmed_scope'} or body['data']['confirmed_scope'] is not True or type(body['data']['provider_reads'])!=bool:raise CRMError('ANALYTICS_INVALID_COMMAND')
  rid=uuid_ref(body['request_id']);data=body['data']
  try:
   first=date.fromisoformat(data['since']);last=date.fromisoformat(data['until'])
   from zoneinfo import ZoneInfo
   if first.isoformat()!=data['since'] or last.isoformat()!=data['until'] or first>last or (last-first).days>365 or last>self.clock().astimezone(ZoneInfo('America/Bogota')).date():raise ValueError()
  except (ValueError,TypeError):raise CRMError('ANALYTICS_DATE_RANGE') from None
  signature=digest({'scope':self.store.scope,'provider':getattr(self.store,'provider',None),'actor':self.actor,'body':body})
  with self.store.transaction():
   self.store.lock();prior=self.store.event(rid)
   if prior:
    self.receipt(rid)
    if prior['fingerprint']!=signature:raise CRMError('ANALYTICS_REQUEST_CONFLICT',409)
    return prior['receipt']|{'replayed':True}
   if len(self.records())>=200:raise CRMError('ANALYTICS_REPORT_LIMIT',409)
   ref=str(uuid.uuid4());d={'id':ref,'code':ref,'title':'Informe comercial '+data['since']+' · '+data['until'],'kind':'REPORT','creator_ref':self.actor,'permission_digest':digest(self.authority().session()['capability_permissions']),'revision':0,'status':'COLLECTING','created_at':self.clock().isoformat(),'query':copy.deepcopy(data),'report':None};self.emit(d,rid,'build',signature,0)
  # Provider reads happen after committing the idempotency reservation, not under a DB lock.
  report=self.collect(data['since'],data['until'],data['provider_reads'],client_factory)
  with self.store.transaction():
   self.store.lock();self.authority();d=copy.deepcopy(self.get(ref));d['report']=report;d['status']=report['state'];return self.emit(d,str(uuid.uuid4()),'source_snapshot',digest(report),d['revision'])

 def recover(self,body):
  from .crm import moment
  if set(body)!={'request_id','operation','job_id','expected_revision','data'} or body['data']!={} or type(body['expected_revision'])!=int:raise CRMError('ANALYTICS_INVALID_COMMAND')
  rid=uuid_ref(body['request_id']);ref=uuid_ref(body['job_id']);signature=digest(body)
  with self.store.transaction():
   self.store.lock();prior=self.store.event(rid)
   if prior:
    self.receipt(rid)
    if prior['fingerprint']!=signature:raise CRMError('ANALYTICS_REQUEST_CONFLICT',409)
    return prior['receipt']|{'replayed':True}
   d=copy.deepcopy(self.get(ref))
   if d['revision']!=body['expected_revision'] or d['status']!='COLLECTING' or moment(d['created_at'])+timedelta(minutes=15)>self.clock():raise CRMError('ANALYTICS_RECOVERY_NOT_DUE',409)
   d['status']='INTERRUPTED';d['report']={'state':'SOURCE_COLLECTION_INCOMPLETE','warnings':['No automatic source retry; prepare a newly confirmed report']}
   return self.emit(d,rid,'recover',signature,d['revision'])
