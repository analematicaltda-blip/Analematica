"""Owned commercial command chain, durable missions, measured tools and engines.

Adapters for Jarvi/Neko/SOUP; canonical general sources remain in Analemática.
No task text becomes Python, SQL, shell, a permission or a provider action.
"""
import copy,json,os,uuid,time,re,hashlib,hmac,secrets
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
from pathlib import Path
from .crm import CRMError,text,digest as base_digest,moment
from .opportunities import uuid_ref
from .contract import SYSTEM
from .army_tools import READ_TOOLS,ALIASES
MAX_RECORDS=500
PREFIX={'sga-cd':'SGA_COMMERCIAL_ARMY','erp-tur':'ERP_COMMERCIAL_ARMY','analematica':'ANA_COMMERCIAL_ARMY'}[SYSTEM]
def digest(value):
 try:return base_digest(value)
 except UnicodeError:raise CRMError('ARMY_INVALID_TEXT') from None
def catalog():
 capabilities=json.loads(Path(__file__).with_name('capabilities.json').read_text());return {**{k:{'mode':'READ','division':v} for k,v in READ_TOOLS.items()},**{v['id']:{'mode':'DOMAIN_WORKFLOW_REQUIRED','division':'CHANNELS'} for v in capabilities}}
def structure():
 nodes=[{'id':SYSTEM+':commercial:'+name,'rank':'GENERAL','parent':None,'name':name,'function':function} for name,function in [('Jarvi','OPERATIONS'),('Neko','CONVERSATION'),('SOUP','AGENT_PROCESS_OPTIMIZATION')]]
 for division in ('CRM','CREATIVE','CHANNELS'):
  parent=nodes[0]['id']
  for rank in ('CORONEL','CAPITAN'):
   key=SYSTEM+':commercial:'+division+':'+rank;nodes.append({'id':key,'rank':rank,'parent':parent,'name':rank+' '+division});parent=key
  for tool,descriptor in catalog().items():
   if descriptor['division']!=division:continue
   previous=parent
   for rank in ('TENIENTE','SARGENTO','SOLDADO'):
    key=SYSTEM+':commercial:'+tool+':'+rank;nodes.append({'id':key,'rank':rank,'parent':previous,'name':rank+' '+tool,'tool':tool});previous=key
 return nodes
def trace(tool,nodes=None):
 nodes={n['id']:n for n in (nodes if nodes is not None else structure())};node=nodes.get(SYSTEM+':commercial:'+tool+':SOLDADO');chain=[]
 while node:
  if node['id'] in chain or len(chain)>=6:raise CRMError('ARMY_CHAIN_INVALID',503)
  chain.append(node['id']);parent=node['parent']
  if parent is not None and parent not in nodes:raise CRMError('ARMY_CHAIN_INVALID',503)
  node=nodes.get(parent)
 return list(reversed(chain))
def dispatch(crm,tool):
 nodes=structure();chain=trace(tool,nodes);by_id={n['id']:n for n in nodes};ranks=('GENERAL','CORONEL','CAPITAN','TENIENTE','SARGENTO','SOLDADO')
 if len(chain)!=len(ranks) or chain[0]!=SYSTEM+':commercial:Jarvi':raise CRMError('ARMY_CHAIN_INVALID',503)
 def delegate(index):
  node=by_id[chain[index]]
  if node['rank']!=ranks[index] or node['parent']!=(chain[index-1] if index else None):raise CRMError('ARMY_CHAIN_INVALID',503)
  crm.authorize()
  if index==len(ranks)-1:
   if node.get('tool')!=tool:raise CRMError('ARMY_CHAIN_INVALID',503)
   from .army_tools import execute
   return execute(crm,tool)
  return delegate(index+1)
 return delegate(0)
class Army:
 def __init__(self,store,crm,clock=None):self.store,self.crm=store,crm;self.actor=crm.actor;self.clock=clock or (lambda:datetime.now(timezone.utc))
 def authority(self):
  access=self.crm.authorize()
  if not access.principal['is_manager']:raise CRMError('ARMY_MANAGER_REQUIRED',403)
  return access
 def raw(self,ref):
  uuid_ref(ref);d=self.store.get(ref)
  if not d:raise CRMError('ARMY_RECORD_NOT_FOUND',404)
  previous='0'*64;events=list(self.store.events(ref))
  for e in events:
   if e.get('previous_event_digest')!=previous or e.get('event_digest')!=digest({k:v for k,v in e.items() if k!='event_digest'}):raise CRMError('ARMY_HISTORY_REVIEW_REQUIRED',503)
   previous=e['event_digest']
  if not events or len(events)!=d['revision'] or previous!=d['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in d.items() if k!='last_event_digest'}):raise CRMError('ARMY_INTEGRITY_REVIEW_REQUIRED',503)
  return d
 def get(self,ref):
  access=self.authority();d=self.raw(ref)
  if d['creator_ref']!=self.actor or d['permission_digest']!=digest(access.session()['capability_permissions']):raise CRMError('ARMY_OWNER_OR_PERMISSIONS_CHANGED',403)
  return d
 def records(self):
  rows=list(self.store.all_jobs())
  if len(rows)>MAX_RECORDS:raise CRMError('ARMY_RECORD_LIMIT',409)
  return [self.raw(r['id']) for r in rows]
 def emit(self,d,rid,op,signature,expected):
  d['revision']=expected+1;d['updated_at']=self.clock().isoformat();receipt={'request_id':rid,'job_id':d['id'],'status':d['status'],'revision':d['revision'],'network_call_by_command':op.startswith('worker_')}
  e={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':d['id'],'operation':op,'fingerprint':signature,'previous_event_digest':d.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in d.items() if k!='last_event_digest'}),'receipt':receipt,'created_at':self.clock().isoformat()};e['event_digest']=digest(e);d['last_event_digest']=e['event_digest'];self.store.save(d,expected);self.store.append(e);return receipt
 def history(self,ref):
  self.get(ref);return {'events':list(self.store.events(ref)),'history_verified':True}
 def receipt(self,rid):
  self.authority();uuid_ref(rid);e=self.store.event(rid)
  if not e or e.get('scope')!=self.store.scope or e.get('provider_ref')!=getattr(self.store,'provider',None) or e.get('actor')!=self.actor:raise CRMError('ARMY_RECEIPT_NOT_FOUND',404)
  self.get(e['item_id']);return e['receipt']|{'previous_receipt_only':True}
 def list(self):
  self.authority();return {'missions':[{k:d[k] for k in ('id','title','status','revision','created_at')} for d in self.records() if d['creator_ref']==self.actor and d['permission_digest']==digest(self.authority().session()['capability_permissions'])],'hierarchy':structure(),'tools':catalog(),'aliases':list(ALIASES),'generals':{'operational':'Jarvi','conversational':'Neko','optimizer':'SOUP'},'voice_agent':{'separate':True,'configured':False,'is_signature':False},'auto_approval':False,'free_sql_or_shell':False,'provider_actions_enabled':False}
 def command(self,body,engine_transport=None):
  self.authority()
  if not isinstance(body,dict) or set(body)!={'request_id','operation','job_id','expected_revision','data'} or type(body['expected_revision'])!=int or not 0<=body['expected_revision']<1000 or not isinstance(body['data'],dict):raise CRMError('ARMY_INVALID_COMMAND')
  rid=uuid_ref(body['request_id']);op=body['operation'];data=body['data'];signature=digest({'system':SYSTEM,'scope':self.store.scope,'provider':getattr(self.store,'provider',None),'actor':self.actor,'body':body});token=None
  with self.store.transaction():
   self.store.lock();self.authority();prior=self.store.event(rid)
   if prior:
    self.receipt(rid)
    if prior['fingerprint']!=signature:raise CRMError('ARMY_REQUEST_CONFLICT',409)
    return prior['receipt']|{'replayed':True}
   if op=='prepare':
    if body['job_id'] is not None or body['expected_revision']!=0 or set(data)!={'question','tools','modality','engine'} or data['modality'] not in ('TEXT','VOICE_TRANSCRIPT') or data['engine'] not in ('none','open-duet','agent-desktop'):raise CRMError('ARMY_INVALID_PREVIEW')
    question=text(data['question'],1000,optional=True);tools=data['tools']
    if not isinstance(tools,list) or len(tools)>8:raise CRMError('ARMY_TOOL_LIMIT')
    interpretation='EXPLICIT_TOOL_SELECTION'
    if not tools:
     if question.strip().casefold() not in ALIASES:raise CRMError('ARMY_NEKO_INTENT_UNSUPPORTED')
     tools=ALIASES[question.strip().casefold()];interpretation='BOUNDED_NEKO_INTENT'
    if not tools or any(not isinstance(t,str) or t not in catalog() for t in tools) or len(set(tools))!=len(tools):raise CRMError('ARMY_TOOL_NOT_ALLOWED')
    if len(self.records())>=200:raise CRMError('ARMY_MISSION_LIMIT',409)
    ref=str(uuid.uuid4());d={'id':ref,'code':ref,'kind':'MISSION','title':'Misión comercial · '+str(len(tools))+' herramientas','tools':sorted(tools),'engine':data['engine'],'modality':data['modality'],'interpretation':interpretation,'question_digest':digest(question),'creator_ref':self.actor,'permission_digest':digest(self.authority().session()['capability_permissions']),'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'revision':0,'status':'PLANNED','created_at':self.clock().isoformat(),'review':None,'authorization':None,'results':[],'engine_result':None,'soup':None,'voice_is_approval':False,'policy_changed_by_agent':False,'provider_action_executed':False,'ledger_written':False}
   else:
    d=copy.deepcopy(self.get(uuid_ref(body['job_id'])))
    if d['creator_ref']!=self.actor:raise CRMError('ARMY_SAME_ADMIN_REQUIRED',403)
    if d['revision']!=body['expected_revision']:raise CRMError('ARMY_REVISION_CONFLICT',409)
    if op=='review' and d['status']=='PLANNED' and data=={'confirmed_plan':True} and type(data['confirmed_plan'])==bool:d['status']='REVIEWED';d['review']={'actor':self.actor,'request_id':rid}
    elif op=='queue' and d['status']=='REVIEWED' and data=={'confirmed_scope':True} and type(data['confirmed_scope'])==bool:d['status']='QUEUED';d['authorization']={'actor':self.actor,'request_id':rid}
    elif op=='cancel' and d['status'] in ('PLANNED','REVIEWED','QUEUED') and not data:d['status']='CANCELLED'
    elif op=='run' and d['status']=='QUEUED' and not data:
     token=secrets.token_hex(32);d['claim_hash']=hashlib.sha256(token.encode()).hexdigest();d['claimed_at']=self.clock().isoformat();d['status']='RUNNING'
    elif op=='recover' and d['status']=='RUNNING' and not data and moment(d['claimed_at'])+timedelta(minutes=15)<=self.clock():d['status']='UNCERTAIN';d['claim_hash']=None;d['engine_result']={'state':'UNKNOWN_NO_AUTO_RETRY'}
    else:raise CRMError('ARMY_STATE_REQUIRED',409)
   receipt=self.emit(d,rid,op,signature,body['expected_revision'])
  if token:return self.execute(d['id'],token,engine_transport)
  return receipt
 def execute(self,ref,token,engine_transport=None):
  d=self.get(ref);results=[]
  from .army_tools import execute
  for tool in d['tools']:
   started=time.perf_counter_ns()
   try:
    self.authority();value=dispatch(self.crm,tool);row={'tool':tool,'status':'SUCCEEDED','evidence':value,'code':None}
   except CRMError as error:
    code=str(error);row={'tool':tool,'status':'BLOCKED','code':code if re.fullmatch('[A-Z0-9_]{1,100}',code) else 'PRECONDITION_REVIEW_REQUIRED','evidence':None}
   except Exception:row={'tool':tool,'status':'BLOCKED','code':'TOOL_REQUIRES_REVIEW','evidence':None}
   row.update(duration_ns=time.perf_counter_ns()-started,chain=trace(tool));results.append(row)
  engine_result={'engine':'none','state':'NOT_REQUESTED'}
  if d['engine']!='none':
   from . import army_engines
   plan={'system':SYSTEM,'instruction':'Revisa únicamente estados de herramientas comerciales; no apruebes ni ejecutes acciones.','tasks':[{'tool':r['tool'],'status':r['status']} for r in results]}
   try:
    self.authority();live=self.get(ref)
    if live['status']!='RUNNING' or not hmac.compare_digest(live['claim_hash'],hashlib.sha256(token.encode()).hexdigest()) or moment(live['claimed_at'])+timedelta(minutes=15)<=self.clock():raise army_engines.EngineUnavailable('Claim no longer valid.')
    engine_result=army_engines.execute(SimpleNamespace(prefix=PREFIX),SimpleNamespace(pk=self.actor),SimpleNamespace(pk=self.store.scope),d['engine'],plan,transport=engine_transport)
   except army_engines.EngineUnavailable:engine_result={'engine':d['engine'],'state':'BLOCKED','code':'ENGINE_DISABLED_OR_UNAVAILABLE'}
   except army_engines.PermissionDenied:engine_result={'engine':d['engine'],'state':'BLOCKED','code':'ENGINE_OWNER_MISMATCH'}
   except army_engines.EngineOutcomeUnknown:engine_result={'engine':d['engine'],'state':'UNCERTAIN','code':'NO_AUTOMATIC_ENGINE_RETRY'}
   except Exception:engine_result={'engine':d['engine'],'state':'BLOCKED','code':'ENGINE_CONFIGURATION_OR_RESPONSE_REVIEW_REQUIRED'}
  with self.store.transaction():
   self.store.lock();current=copy.deepcopy(self.get(ref))
   if current['status']!='RUNNING' or not hmac.compare_digest(current['claim_hash'],hashlib.sha256(token.encode()).hexdigest()):raise CRMError('ARMY_CLAIM_REQUIRED',409)
   current['results']=results;current['engine_result']=engine_result;current['claim_hash']=None
   succeeded=sum(r['status']=='SUCCEEDED' for r in results);current['status']='SUCCEEDED' if succeeded==len(results) else 'PARTIAL' if succeeded else 'BLOCKED'
   if engine_result.get('state') in ('UNCERTAIN','UNKNOWN_NO_AUTO_RETRY'):current['status']='UNCERTAIN'
   elif engine_result.get('state')=='QUEUED':current['status']='ENGINE_QUEUED'
   elif engine_result.get('state')=='BLOCKED' and current['status']=='SUCCEEDED':current['status']='PARTIAL'
   current['soup']=self.optimize(results)
   return self.emit(current,str(uuid.uuid4()),'worker_result',digest({'mission':ref,'results':results,'engine':engine_result}),current['revision'])
 def optimize(self,results):
  return {'general':'SOUP','scope':'AGENT_PROCESS_OPTIMIZATION','samples':[{'tool':r['tool'],'duration_ns':r['duration_ns'],'status':r['status']} for r in results],'recommendations':[{'tool':r['tool'],'code':'RESOLVE_PRECONDITION' if r['status']=='BLOCKED' else 'PROFILE_LATENCY','automatic_change_allowed':False} for r in results if r['status']=='BLOCKED' or r['duration_ns']>250000000],'policy_changed':False,'training_executed':False,'candidate_promoted':False,'advertising_optimization_performed':False,'quality_scope':'Observed tools, not model accuracy or end-to-end SLA'}
