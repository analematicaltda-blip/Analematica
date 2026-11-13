"""Durable, private generation jobs. A worker generates; a human reviews; nothing publishes."""
import copy,hashlib,hmac,json,secrets,uuid
from datetime import datetime,timedelta,timezone
from .crm import CRMError,text,digest,moment
from .opportunities import uuid_ref
from .generation_providers import profiles
MAX_JOBS=200
MAX_DAILY=20
MAX_DAILY_UNITS=2000000
MAX_BYTES=64*1024*1024
STATES={'QUEUED','RUNNING','SUCCEEDED','REVIEWED','FAILED','UNCERTAIN','CANCELLED'}
class Generation:
    def __init__(self,store,crm,clock=None):self.store,self.crm,self.actor=store,crm,crm.actor;self.clock=clock or (lambda:datetime.now(timezone.utc))
    def authority(self):
        access=self.crm.authorize()
        if not access.principal['is_manager'] or not access.session()['capability_permissions'].get('media.image.generate'):raise CRMError('GENERATION_ADMINISTRATOR_REQUIRED',403)
    def video_authority(self):
        if not self.crm.authorize().session()['capability_permissions'].get('media.reel.render'):raise CRMError('VIDEO_RENDER_PERMISSION_REQUIRED',403)
    def profiles(self):
        self.authority();rows=list(profiles(self.store.scope,getattr(self.store,'provider',None)).values());return {'profiles':rows,'external_calls_enabled':any(p['remote_required'] and p['execution_allowed'] for p in rows),'worker_required':True,'cost_is_money':False,'runtime_qualified':False,'catalog':json.loads(__import__('pathlib').Path(__file__).with_name('generation_catalog.json').read_text())}
    def get(self,ref):
        self.authority();uuid_ref(ref);item=self.store.get(ref)
        if not item:raise CRMError('GENERATION_JOB_NOT_FOUND',404)
        if item.get('kind')=='VIDEO':self.video_authority()
        events=list(self.store.events(ref));previous='0'*64
        for event in events:
            if event.get('previous_event_digest')!=previous or event.get('event_digest')!=digest({k:v for k,v in event.items() if k!='event_digest'}):raise CRMError('GENERATION_HISTORY_REVIEW_REQUIRED',503)
            previous=event['event_digest']
        if not events or len(events)!=item['revision'] or previous!=item['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in item.items() if k!='last_event_digest'}):raise CRMError('GENERATION_INTEGRITY_REVIEW_REQUIRED',503)
        return item
    def view(self,ref):return {k:v for k,v in self.get(ref).items() if k!='claim_token_hash'}
    def summary(self,item):return {k:item[k] for k in ('id','title','kind','status','revision','created_at','updated_at','cost','error_code')}
    def list(self,offset=0):
        self.authority()
        if type(offset)!=int or not 0<=offset<=MAX_JOBS:raise CRMError('INVALID_PAGE')
        rows,more=self.store.list('','',offset,30)
        return {'jobs':[self.summary(self.get(x['id'])) for x in rows],'next_offset':offset+30 if more else None,'cost_is_money':False,'runtime_qualified':False}
    def receipt(self,rid):
        self.authority();uuid_ref(rid);event=self.store.event(rid)
        if not event or event.get('scope')!=self.store.scope or event.get('provider_ref')!=getattr(self.store,'provider',None) or event.get('actor')!=self.actor:raise CRMError('RECEIPT_NOT_FOUND',404)
        if event.get('event_digest')!=digest({k:v for k,v in event.items() if k!='event_digest'}):raise CRMError('GENERATION_HISTORY_REVIEW_REQUIRED',503)
        return {**event['receipt'],'previous_receipt_only':True}
    def history(self,ref):
        self.get(ref);return {'events':list(self.store.events(ref)),'history_verified':True}
    def record(self,item,rid,operation,signature,expected):
        item['revision']=expected+1;item['updated_at']=self.clock().isoformat()
        receipt={'job_id':item['id'],'status':item['status'],'revision':item['revision'],'published':False,'money_charged':False}
        event={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':item['id'],'operation':operation,'fingerprint':signature,'previous_event_digest':item.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in item.items() if k!='last_event_digest'}),'created_at':self.clock().isoformat(),'receipt':receipt}
        event['event_digest']=digest(event);item['last_event_digest']=event['event_digest'];self.store.save(item,expected);self.store.append(event);return receipt
    def _jobs(self):return [self.get(j['id']) for j in self.store.all_jobs()]
    def command(self,body):
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','job_id','expected_revision','data'} or not isinstance(body['data'],dict):raise CRMError('INVALID_GENERATION_COMMAND')
        rid=uuid_ref(body['request_id']);op=body['operation'];rev=body['expected_revision'];data=body['data']
        if type(rev)!=int or not 0<=rev<20 or len(json.dumps(data).encode())>20000:raise CRMError('INVALID_GENERATION_COMMAND')
        signature=digest({'domain':'GENERATION','scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'body':body})
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior.get('fingerprint')!=signature:raise CRMError('GENERATION_REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            if op=='create':
                if body['job_id'] is not None or rev!=0 or set(data)!={'title','kind','prompt','profile_id','max_cost_units','confirmed_input_rights'} or data['confirmed_input_rights'] is not True:raise CRMError('INVALID_GENERATION_CREATE')
                if data['kind'] not in ('SCRIPT','COPY','IMAGE','VIDEO') or not isinstance(data['profile_id'],str):raise CRMError('INVALID_GENERATION_KIND')
                profile=profiles(self.store.scope,getattr(self.store,'provider',None)).get(data['profile_id'])
                if not profile or data['kind'] not in profile['kinds']:raise CRMError('GENERATION_PROFILE_REQUIRED',503)
                if not profile['execution_allowed']:raise CRMError('GENERATION_REMOTE_APPROVAL_REQUIRED',503)
                if type(data['max_cost_units'])!=int or not profile['cost_units']<=data['max_cost_units']<=MAX_DAILY_UNITS:raise CRMError('GENERATION_BUDGET_APPROVAL_REQUIRED',409)
                jobs=self._jobs();today=self.clock().date();daily=[j for j in jobs if moment(j['created_at']).date()==today]
                if len(jobs)>=MAX_JOBS or len(daily)>=MAX_DAILY or sum(j['cost']['reserved_units'] for j in daily if j['cost']['state']!='RELEASED')+profile['cost_units']>MAX_DAILY_UNITS or sum(j.get('result',{}).get('size',0) if j.get('result') else 0 for j in jobs)>=MAX_BYTES:raise CRMError('GENERATION_QUOTA_EXCEEDED',409)
                prompt=text(data['prompt'],3000)
                if data['kind']=='VIDEO':
                    self.video_authority()
                    from .video_composition import spec
                    try:spec(json.loads(prompt))
                    except (ValueError,TypeError):raise CRMError('VIDEO_INVALID_COMPOSITION') from None
                if len(prompt.encode())>12000:raise CRMError('GENERATION_PROMPT_LIMIT')
                ref=str(uuid.uuid4());item={'id':ref,'code':ref,'title':text(data['title'],150),'kind':data['kind'],'prompt':prompt,'profile':profile,'scope':self.store.scope,'creator_ref':self.actor,'provider_ref':getattr(self.store,'provider',None),'created_at':self.clock().isoformat(),'updated_at':self.clock().isoformat(),'revision':0,'status':'QUEUED','cost':{'unit':'LOCAL_CREDIT','basis':'OPERATOR_ESTIMATE','reserved_units':profile['cost_units'],'actual_money':None,'state':'RESERVED'},'result':None,'trace':None,'review':None,'error_code':None,'claim_token_hash':None,'lease_expires_at':None,'attempt':0,'input_rights_declared':True,'rights_authenticity_verified':False,'published':False}
            else:
                item=copy.deepcopy(self.get(uuid_ref(body['job_id'])))
                if item['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
                if op=='cancel' and not data and item['status']=='QUEUED':item['status']='CANCELLED';item['cost']['state']='RELEASED'
                elif op=='recover' and not data and item['status']=='RUNNING' and moment(item['lease_expires_at'])<=self.clock():item['status']='UNCERTAIN';item['error_code']='GENERATION_WORKER_RESULT_UNCERTAIN';item['cost']['state']='UNKNOWN';item['claim_token_hash']=None
                elif op=='review' and set(data)=={'confirmed_content','confirmed_rights','note'} and data['confirmed_content'] is True and data['confirmed_rights'] is True and item['status']=='SUCCEEDED':
                    self.bytes(item['id']);item['status']='REVIEWED';item['review']={'actor':self.actor,'at':self.clock().isoformat(),'note':text(data['note'],500),'rights_declared':True,'rights_authenticity_verified':False}
                else:raise CRMError('GENERATION_STATE_OR_REVIEW_REQUIRED',409)
            return self.record(item,rid,op,signature,rev)
    def claim(self,ref):
        self.authority()
        with self.store.transaction():
            self.authority();self.store.lock();item=copy.deepcopy(self.get(ref))
            if item['status']!='QUEUED' or item['creator_ref']!=self.actor:raise CRMError('GENERATION_JOB_NOT_CLAIMABLE',409)
            current=profiles(self.store.scope,getattr(self.store,'provider',None)).get(item['profile']['id'])
            if not current or not current['execution_allowed'] or current['configuration_digest']!=item['profile']['configuration_digest']:
                item['status']='FAILED';item['error_code']='GENERATION_CONFIGURATION_CHANGED';item['cost']['state']='RELEASED';return self.record(item,str(uuid.uuid4()),'configuration_blocked','worker',item['revision']),None
            if any(j['status']=='RUNNING' for j in self._jobs()):raise CRMError('GENERATION_COMPANY_BUSY',409)
            token=secrets.token_urlsafe(32);item['claim_token_hash']=hashlib.sha256(token.encode()).hexdigest();item['status']='RUNNING';item['attempt']=1;item['lease_expires_at']=(self.clock()+timedelta(minutes=15)).isoformat();self.record(item,str(uuid.uuid4()),'claimed','worker',item['revision']);return item,token
    def finish(self,ref,token,result=None,error_code=None):
        self.authority()
        with self.store.transaction():
            self.authority();self.store.lock();item=copy.deepcopy(self.get(ref));expected=hashlib.sha256(str(token).encode()).hexdigest()
            if item['status']!='RUNNING' or item['creator_ref']!=self.actor or not hmac.compare_digest(item.get('claim_token_hash') or '',expected):raise CRMError('GENERATION_STALE_WORKER',409)
            item['claim_token_hash']=None
            if moment(item['lease_expires_at'])<=self.clock():item['status']='UNCERTAIN';item['error_code']='GENERATION_WORKER_RESULT_UNCERTAIN';item['cost']['state']='UNKNOWN'
            elif error_code:
                allowed={'GENERATION_PROVIDER_REJECTED','GENERATION_PROVIDER_RESPONSE_LIMIT','GENERATION_PROVIDER_UNAVAILABLE_OR_INVALID','GENERATION_LOCAL_MODEL_NOT_QUALIFIED','GENERATION_INVALID_TEXT_RESULT','GENERATION_INVALID_USAGE','GENERATION_LOCAL_MODEL_CHANGED','GENERATION_INVALID_IMAGE_RESULT','GENERATION_ADAPTER_UNAVAILABLE','GENERATION_WORKER_FAILED','GENERATION_SECRET_BINDING_REQUIRED','GENERATION_REMOTE_APPROVAL_REQUIRED','GENERATION_ENDPOINT_CONFIGURATION_REQUIRED','VIDEO_RENDERER_REQUIRED','VIDEO_RENDERER_CHANGED','VIDEO_AUDIO_REVIEW_STALE','VIDEO_AUDIO_AUTHORIZATION_REQUIRED','VIDEO_AUDIO_DURATION_OR_STREAM_INVALID','VIDEO_COMPOSITION_FAILED'}
                item['status']='FAILED';item['error_code']=error_code if error_code in allowed else 'GENERATION_WORKER_FAILED';item['cost']['state']='UNKNOWN'
            else:
                raw,mime,trace=result
                if item['kind']=='VIDEO':
                    from .video_composition import sources,spec
                    checked=sources(self.crm,spec(json.loads(item['prompt'])))
                    if not isinstance(trace,dict) or trace.get('composition') is not True or trace.get('generative_video') is not False or trace.get('audio_source_hashes')!={k:hashlib.sha256(v).hexdigest() for k,v in checked.items()}:raise CRMError('VIDEO_AUDIO_REVIEW_STALE',409)
                if not isinstance(raw,bytes) or not 0<len(raw)<=8*1024*1024 or mime!={'COPY':'text/plain','SCRIPT':'text/plain','IMAGE':'image/png','VIDEO':'video/mp4'}[item['kind']] or not isinstance(trace,dict) or trace.get('model_digest')!=item['profile']['model_digest']:raise CRMError('GENERATION_INVALID_WORKER_RESULT',503)
                size=sum(j.get('result',{}).get('size',0) if j.get('result') else 0 for j in self._jobs())
                if size+len(raw)>MAX_BYTES:raise CRMError('GENERATION_QUOTA_EXCEEDED',409)
                checksum=hashlib.sha256(raw).hexdigest();self.store.save_result(ref,raw,mime,checksum);item['result']={'sha256':checksum,'mime':mime,'size':len(raw)};item['trace']=trace;item['status']='SUCCEEDED';item['cost']['state']='CONSUMED_ESTIMATE'
            return self.record(item,str(uuid.uuid4()),'worker_finished','worker',item['revision'])
    def bytes(self,ref):
        item=self.get(ref)
        if item['status'] not in ('SUCCEEDED','REVIEWED'):raise CRMError('GENERATION_RESULT_NOT_READY',409)
        row=self.store.result(ref)
        if not row or row['sha256']!=item['result']['sha256'] or hashlib.sha256(row['data']).hexdigest()!=row['sha256'] or row['mime']!=item['result']['mime']:raise CRMError('GENERATION_RESULT_INTEGRITY_REVIEW_REQUIRED',503)
        return row['data'],row['mime']
