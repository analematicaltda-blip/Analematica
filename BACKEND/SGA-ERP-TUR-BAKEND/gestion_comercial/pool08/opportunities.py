"""Owned sales pipeline: commercial states never certify payment or accounting."""
import json
import re
import uuid
from datetime import datetime,timezone,timedelta
from decimal import Decimal,InvalidOperation
from .crm import CRMError,text,moment,digest

STAGES={'NEW':('CONTACTED','LOST'),'CONTACTED':('NEW','QUALIFIED','LOST'),
        'QUALIFIED':('CONTACTED','PROPOSAL','LOST'),'PROPOSAL':('QUALIFIED','NEGOTIATION','LOST'),
        'NEGOTIATION':('PROPOSAL','WON','LOST'),'WON':(),'LOST':()}
CURRENCIES=('COP','USD','EUR','GBP','CAD','BRL','MXN','PEN','CLP','ARS')
LOSSES=('PRICE','TIMING','COMPETITOR','NO_CONTACT','CANCELLED','OTHER')
FALSE_FINANCIAL={'payment_verified':False,'invoice_issued':False,'ledger_written':False,'revenue_recognized':False}
RULE_VERSION='commercial-priority-v1'

def uuid_ref(value):
    try:
        if str(uuid.UUID(value))!=value:raise ValueError()
    except (ValueError,TypeError,AttributeError):raise CRMError('INVALID_REQUEST_ID') from None
    return value

def money(value):
    if not isinstance(value,str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,15})\.[0-9]{2}',value):raise CRMError('INVALID_MONEY')
    result=Decimal(value)
    if result>Decimal('9999999999999999.99'):raise CRMError('INVALID_MONEY')
    return value

def evidence(value):
    if not isinstance(value,str) or not re.fullmatch('[a-f0-9]{64}',value):raise CRMError('EVIDENCE_DIGEST_REQUIRED')
    return value

class Opportunities:
    def __init__(self,store,crm):self.store,self.crm,self.actor=store,crm,crm.actor
    def contact(self,ref):
        if not isinstance(ref,str) or len(ref)>96:raise CRMError('INVALID_CONTACT_ID')
        return self.crm.get(ref)
    def require_member(self,ref):
        text(ref,96)
        if not self.crm.member(ref):raise CRMError('RESPONSIBLE_NOT_IN_COMPANY',403)
        return ref
    def next_action(self,value):
        if value is None:return None
        if not isinstance(value,dict) or set(value)!={'description','due_at','responsible_ref'}:raise CRMError('INVALID_NEXT_ACTION')
        due=moment(value['due_at'])
        if due>datetime.now(timezone.utc)+timedelta(days=366):raise CRMError('INVALID_NEXT_ACTION_DATE')
        return {'description':text(value['description'],300),'due_at':due.isoformat(),'responsible_ref':self.require_member(value['responsible_ref'])}
    def score(self,item):
        if item.get('requires_adoption'):
            return {'status':'NOT_CALIBRATED','kind':'RULE_BASED_PRIORITY','model_version':RULE_VERSION,'value':None,'probability':None,'reason':'LEGACY_REVIEW_REQUIRED','criteria':[]}
        contact=self.contact(item['contact_id']);now=datetime.now(timezone.utc)
        action=item.get('next_action');due=bool(action and moment(action['due_at'])>=now)
        observations=[('contact_channel',20,bool(contact['email'] or contact['phone']),{'kind':'CRM_CONTACT','ref':contact['id']}),
                      ('active_responsible',20,bool(self.crm.member(item['responsible_ref'])),{'kind':'LOCAL_MEMBERSHIP','ref':item['responsible_ref']}),
                      ('scheduled_next_action',20,due,{'kind':'OPPORTUNITY_FIELD','ref':item['id']+':next_action'}),
                      ('declared_interest_support',25,bool(item.get('interest_evidence')),{'kind':'DECLARED_DIGEST','ref':item.get('interest_evidence'),'authenticity_verified':False}),
                      ('declared_value',15,Decimal(item['value'])>0,{'kind':'OPPORTUNITY_FIELD','ref':item['id']+':value','source':'MANUAL_DECLARATION'})]
        withdrawn=contact['status']=='WITHDRAWN'
        inactive=withdrawn or item['stage'] in ('WON','LOST')
        criteria=[{'id':key,'weight':weight,'observed':observed,'points':weight if observed and not inactive else 0,'source':source} for key,weight,observed,source in observations]
        return {'status':'NOT_CALIBRATED','kind':'RULE_BASED_PRIORITY','model_version':RULE_VERSION,'value':sum(c['points'] for c in criteria),
                'probability':None,'accuracy':None,'dataset_evaluated':False,'evaluated_at':now.isoformat(),'contact_withdrawn':withdrawn,'criteria':criteria}
    def present(self,item):
        if not item.get('requires_adoption'):
            event=self.store.last_event(item['id'])
            unsigned={k:v for k,v in (event or {}).items() if k!='event_digest'}
            result=digest({k:v for k,v in item.items() if k!='last_event_digest'})
            if not event or event['event_digest']!=item['last_event_digest'] or event['event_digest']!=digest(unsigned) or event['result_digest']!=result:
                raise CRMError('OPPORTUNITY_INTEGRITY_REVIEW_REQUIRED',503)
        score=self.score(item);allowed=list(STAGES.get(item['stage'],()))
        if score.get('contact_withdrawn'):allowed=[value for value in allowed if value=='LOST']
        return {**item,'score':score,'allowed_transitions':allowed,**FALSE_FINANCIAL}
    def list(self,q='',stage='',offset=0,limit=30):
        self.crm.authorize()
        if not isinstance(q,str) or len(q)>200 or stage not in ('',*STAGES) or type(offset)!=int or not 0<=offset<=100000 or type(limit)!=int or not 1<=limit<=100:raise CRMError('INVALID_PAGE')
        rows,more=self.store.list(q,stage,offset,limit)
        return {'context':{'actor_ref':self.actor,'tenant_ref':self.store.scope},'opportunities':[self.present(item) for item in rows],
                'next_offset':offset+limit if more else None,'stages':{key:list(value) for key,value in STAGES.items()},'currencies':list(CURRENCIES),'loss_codes':list(LOSSES),**FALSE_FINANCIAL}
    def get(self,ref):
        self.crm.authorize();uuid_ref(ref)
        item=self.store.get(ref)
        if item is None:raise CRMError('OPPORTUNITY_NOT_FOUND',404)
        return self.present(item)
    def history(self,ref,offset=0):
        initial=self.get(ref)
        if type(offset)!=int or not 0<=offset<=100000:raise CRMError('INVALID_PAGE')
        previous='0'*64;events=[]
        for event in self.store.events(ref):
            unsigned={k:v for k,v in event.items() if k!='event_digest'}
            if event['previous_event_digest']!=previous or event['event_digest']!=digest(unsigned):raise CRMError('OPPORTUNITY_HISTORY_REVIEW_REQUIRED',503)
            previous=event['event_digest'];events.append(event)
        item=self.store.get(ref)
        if item['revision']!=initial['revision']:raise CRMError('HISTORY_CHANGED_RETRY',409)
        if not item.get('requires_adoption') and previous!=item['last_event_digest']:raise CRMError('OPPORTUNITY_HISTORY_REVIEW_REQUIRED',503)
        legacy=self.store.legacy_history(ref)
        return {'events':events[offset:offset+5],'legacy_events':legacy[offset:offset+5],'next_offset':offset+5 if max(len(events),len(legacy))>offset+5 else None,'history_verified':True,'legacy_authenticity_verified':False}
    def receipt(self,rid):
        self.crm.authorize();uuid_ref(rid);event=self.store.event(rid)
        if event is None or event['scope']!=self.store.scope or event['actor']!=self.actor:raise CRMError('RECEIPT_NOT_FOUND',404)
        if event['event_digest']!=digest({k:v for k,v in event.items() if k!='event_digest'}):raise CRMError('OPPORTUNITY_HISTORY_REVIEW_REQUIRED',503)
        return {**event['receipt'],'previous_receipt_only':True}
    def values(self,data,current=None):
        item={key:(current or {}).get(key) for key in ('title','value','currency','responsible_ref','notes','next_action','interest_evidence')}
        item.update({k:v for k,v in data.items() if k in item})
        item['title']=text(item['title'],200);item['value']=money(item['value'])
        if item['currency'] not in CURRENCIES:raise CRMError('INVALID_CURRENCY')
        item['responsible_ref']=self.require_member(item['responsible_ref']);item['notes']=text(item.get('notes') or '',2000,True)
        item['next_action']=self.next_action(item.get('next_action'))
        if item.get('interest_evidence') is not None:item['interest_evidence']=evidence(item['interest_evidence'])
        return item
    def command(self,body):
        self.crm.authorize()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','opportunity_id','expected_revision','data'}:raise CRMError('INVALID_COMMAND')
        rid=uuid_ref(body['request_id']);operation=body['operation'];ref=body['opportunity_id'];revision=body['expected_revision'];data=body['data']
        if type(revision)!=int or not 0<=revision<2**31 or not isinstance(data,dict) or len(json.dumps(data).encode())>12000:raise CRMError('INVALID_COMMAND')
        signature=digest({'scope':self.store.scope,'actor':self.actor,'domain':'OPPORTUNITY','body':body})
        with self.store.transaction():
            self.crm.authorize();self.store.lock()
            prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature or prior['scope']!=self.store.scope:raise CRMError('REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            previous_stage=None;previous_event='0'*64;legacy_snapshot=None
            if operation=='create':
                if ref is not None or revision!=0 or set(data)-{'contact_id','title','value','currency','responsible_ref','notes','next_action','interest_evidence'}:raise CRMError('INVALID_CREATE')
                contact=self.contact(data.get('contact_id'))
                if contact['status']=='WITHDRAWN':raise CRMError('CONTACT_WITHDRAWN',409)
                item={**self.values(data),'id':str(uuid.uuid4()),'revision':1,'contact_id':contact['id'],'stage':'NEW','loss_code':None,'loss_detail':None,'tasks':[],'win_evidence':None,'requires_adoption':False}
            else:
                uuid_ref(ref);old=self.store.get(ref)
                if old is None:raise CRMError('OPPORTUNITY_NOT_FOUND',404)
                if old['revision']!=revision:raise CRMError('REVISION_CONFLICT',409)
                if not old.get('requires_adoption'):self.history(ref)
                item=json.loads(json.dumps(old));previous_stage=old['stage'];previous_event=old.get('last_event_digest','0'*64)
                if item.get('requires_adoption'):
                    if operation!='adopt':raise CRMError('LEGACY_OPPORTUNITY_REVIEW_REQUIRED',409)
                    if set(data)-{'contact_id','currency','responsible_ref','review_reason','evidence_digest','loss_code','loss_detail','next_action','review_stage'}:raise CRMError('INVALID_ADOPTION')
                    contact=self.contact(data.get('contact_id'));text(data.get('review_reason'),500);evidence(data.get('evidence_digest'))
                    if contact['status']=='WITHDRAWN':raise CRMError('CONTACT_WITHDRAWN',409)
                    if item['stage'] not in STAGES:
                        if not isinstance(data.get('review_stage'),str) or data.get('review_stage') not in STAGES or not getattr(self.crm.authorize(),'principal',{}).get('is_manager'):
                            raise CRMError('LEGACY_STAGE_REVIEW_REQUIRED',409)
                        item['stage']=data['review_stage']
                    elif 'review_stage' in data:raise CRMError('INVALID_ADOPTION')
                    legacy_snapshot=item.pop('legacy_snapshot');item.update(self.values({**item,**data,'notes':''}))
                    item.update(contact_id=contact['id'],requires_adoption=False,loss_code=None,loss_detail=None,tasks=[],win_evidence=None)
                    if item['stage']=='LOST':self.loss(item,data)
                    if item['stage']=='WON':item['win_evidence']=data['evidence_digest']
                else:
                    contact=self.contact(item['contact_id'])
                    if contact['status']=='WITHDRAWN' and not (operation=='transition' and data.get('stage')=='LOST'):raise CRMError('CONTACT_WITHDRAWN',409)
                    if operation=='update':
                        if not data or set(data)-{'title','value','currency','responsible_ref','notes','next_action','interest_evidence'}:raise CRMError('INVALID_UPDATE')
                        if item['stage'] in ('WON','LOST'):raise CRMError('REOPEN_REQUIRED',409)
                        item.update(self.values(data,item))
                    elif operation=='transition':
                        if set(data)-{'stage','reason','loss_code','loss_detail','confirmation','evidence_digest'}:raise CRMError('INVALID_TRANSITION')
                        target=data.get('stage');text(data.get('reason'),500)
                        if target not in STAGES.get(item['stage'],()):raise CRMError('TRANSITION_NOT_ALLOWED',409)
                        if target=='LOST':self.loss(item,data)
                        elif 'loss_code' in data or 'loss_detail' in data:raise CRMError('INVALID_LOSS_FIELDS')
                        if target=='WON':
                            if data.get('confirmation') is not True:raise CRMError('COMMERCIAL_CONFIRMATION_REQUIRED')
                            item['win_evidence']=evidence(data.get('evidence_digest'))
                        elif 'confirmation' in data or 'evidence_digest' in data:raise CRMError('INVALID_WIN_FIELDS')
                        item['stage']=target
                    elif operation=='reopen':
                        if set(data)!={'reason'} or item['stage'] not in ('WON','LOST'):raise CRMError('INVALID_REOPEN')
                        text(data['reason'],500)
                        authority=self.crm.authorize()
                        if not getattr(authority,'principal',{}).get('is_manager'):raise CRMError('LOCAL_ADMINISTRATOR_REQUIRED',403)
                        item.update(stage='NEW',loss_code=None,loss_detail=None,win_evidence=None)
                    elif operation=='task':
                        if set(data)!={'title','due_at','responsible_ref'} or len(item['tasks'])>=100:raise CRMError('INVALID_TASK')
                        item['tasks'].append({'id':rid,'title':text(data['title'],200),'due_at':moment(data['due_at']).isoformat(),'responsible_ref':self.require_member(data['responsible_ref']),'completed':False})
                    elif operation=='complete_task':
                        if set(data)!={'task_id'}:raise CRMError('INVALID_TASK')
                        task=next((t for t in item['tasks'] if t['id']==data['task_id']),None)
                        if task is None:raise CRMError('TASK_NOT_FOUND',404)
                        task['completed']=True
                    else:raise CRMError('UNKNOWN_OPERATION')
                item['revision']=revision+1
            item.update(FALSE_FINANCIAL);item['updated_at']=datetime.now(timezone.utc).isoformat()
            result_digest=digest({k:v for k,v in item.items() if k!='last_event_digest'})
            receipt={'opportunity_id':item['id'],'revision':item['revision'],'stage':item['stage'],'replayed':False,**FALSE_FINANCIAL}
            event={'id':rid,'scope':self.store.scope,'actor':self.actor,'opportunity_id':item['id'],'operation':operation,'fingerprint':signature,
                   'previous_event_digest':previous_event,'previous_revision':revision,'previous_stage':previous_stage,'stage':item['stage'],
                   'data':data,'result_digest':result_digest,'created_at':item['updated_at'],'receipt':receipt}
            if legacy_snapshot is not None:event['legacy_snapshot']=legacy_snapshot
            event['event_digest']=digest(event);item['last_event_digest']=event['event_digest']
            self.store.save(item,revision);self.store.append(event)
        return receipt
    def loss(self,item,data):
        if data.get('loss_code') not in LOSSES:raise CRMError('LOSS_REASON_REQUIRED')
        item['loss_code']=data['loss_code'];item['loss_detail']=text(data.get('loss_detail'),500)
