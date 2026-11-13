"""Commercial CRM rules. Persistence and live membership belong to each backend."""
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone, timedelta

class CRMError(ValueError):
    def __init__(self, code, status=422, **safe):
        self.code, self.status, self.safe = code, status, safe
        super().__init__(code)

def text(value, limit, optional=False):
    if not isinstance(value,str) or len(value)>limit or (not optional and not value.strip()) or any(ord(c)<32 and c not in '\n\t' for c in value):
        raise CRMError('INVALID_TEXT')
    return value.strip()

def digest(value):
    try:return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    except UnicodeError:raise CRMError('INVALID_TEXT_ENCODING') from None

def moment(value):
    try: result=datetime.fromisoformat(value.replace('Z','+00:00'))
    except (ValueError,TypeError,AttributeError): raise CRMError('INVALID_DATE') from None
    if result.tzinfo is None: raise CRMError('TIMEZONE_REQUIRED')
    return result.astimezone(timezone.utc)

class CRM:
    def __init__(self, store, *, actor, authorize, member):
        self.store,self.actor,self.authorize,self.member=store,str(actor),authorize,member

    def context(self):
        authority=self.authorize()
        return {'system':self.store.system,'actor_ref':self.actor,'tenant_ref':self.store.scope,'company_name':self.store.company_name,'members':self.member(None),
                'can_prepare_offers':bool(authority.session()['capability_permissions'].get('quote.prepare')),'can_manage_catalog':bool(getattr(authority,'principal',{}).get('is_manager')),'roles_preserved':True,'can_manage_opportunities':bool(getattr(authority,'principal',{}).get('is_manager')),'delivery_authorized':False}

    def list(self,query='',offset=0,limit=50):
        self.authorize()
        if not isinstance(query,str) or len(query)>200 or type(offset)!=int or offset<0 or offset>100000 or type(limit)!=int or not 1<=limit<=100:
            raise CRMError('INVALID_PAGE')
        rows,more=self.store.list(query,offset,limit)
        summary_keys=('id','name','email','phone','origin','responsible_ref','status','revision','customer_ref','stage')
        return {'context':{'tenant_ref':self.store.scope,'actor_ref':self.actor},'contacts':[{k:row[k] for k in summary_keys} for row in rows],'offset':offset,'next_offset':offset+limit if more else None}

    def get(self,contact):
        self.authorize()
        result=self.store.get(contact)
        if result is None: raise CRMError('CONTACT_NOT_FOUND',404)
        return result

    def history(self,contact,offset=0):
        self.get(contact)
        if type(offset)!=int or not 0<=offset<=100000: raise CRMError('INVALID_PAGE')
        rows=self.store.history(contact,offset,21)
        return {'events':rows[:20],'offset':offset,'next_offset':offset+20 if len(rows)>20 else None}

    def receipt(self,request_id):
        self.authorize()
        try:
            if str(uuid.UUID(request_id))!=request_id:raise ValueError()
        except (TypeError,ValueError,AttributeError):raise CRMError('INVALID_REQUEST_ID') from None
        event=self.store.event(request_id)
        if event is None or event['scope']!=self.store.scope or event.get('actor')!=self.actor:
            raise CRMError('RECEIPT_NOT_FOUND',404)
        return {**event['receipt'],'previous_receipt_only':True}

    def normalized(self,data,current=None):
        result={key:(current or {}).get(key,'') for key in ('name','email','phone','origin','responsible_ref','notes')}
        for key,value in data.items():
            if key in result: result[key]=value
        for key,maximum in [('name',150),('origin',100),('responsible_ref',96),('notes',2000)]:
            result[key]=text(result[key],maximum,key=='notes')
        if not isinstance(result['email'],str) or not isinstance(result['phone'],str): raise CRMError('INVALID_CONTACT')
        result['email']=result['email'].strip().casefold()
        result['phone']=re.sub(r'[ ()-]','',result['phone'])
        if any(ord(c)<32 or 127<=ord(c)<=159 for c in result['email']) or len(result['email'])>254 or (result['email'] and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',result['email'])) or (result['phone'] and not re.fullmatch(r'\+?[0-9]{7,15}',result['phone'])): raise CRMError('INVALID_CONTACT')
        if not self.member(result['responsible_ref']): raise CRMError('RESPONSIBLE_NOT_IN_COMPANY',403)
        return result

    def duplicates(self,values,contact,review):
        candidates=self.store.duplicates(values['email'],values['phone'],contact)
        if candidates:
            if (not isinstance(review,dict) or set(review)!={'candidate_ids','reason'} or
                not isinstance(review['candidate_ids'],list) or any(not isinstance(x,str) for x in review['candidate_ids']) or
                sorted(review['candidate_ids'])!=sorted(candidates)):
                raise CRMError('DUPLICATE_REVIEW_REQUIRED',409,candidate_ids=candidates)
            text(review['reason'],500)
        elif review is not None: raise CRMError('STALE_DUPLICATE_REVIEW',409)

    def command(self,body):
        self.authorize()
        if not isinstance(body,dict) or set(body)-{'request_id','operation','contact_id','expected_revision','data'}: raise CRMError('INVALID_COMMAND')
        request_id=body.get('request_id')
        try:
            if str(uuid.UUID(request_id))!=request_id: raise ValueError()
        except (TypeError,ValueError,AttributeError): raise CRMError('INVALID_REQUEST_ID') from None
        operation,contact,revision,data=(body.get(key) for key in ('operation','contact_id','expected_revision','data'))
        if type(revision)!=int or revision<0 or revision>=2**31 or not isinstance(data,dict): raise CRMError('INVALID_COMMAND')
        fingerprint=digest({'actor':self.actor,'scope':self.store.scope,'command':body})
        with self.store.transaction():
            self.authorize()  # Fresh DB authority inside the same unit of work.
            self.store.lock()
            prior=self.store.event(request_id)
            if prior:
                if prior['fingerprint']!=fingerprint or prior['scope']!=self.store.scope: raise CRMError('REQUEST_CONFLICT',409)
                return {**prior['receipt'],'replayed':True,'previous_receipt_only':True}
            original=None
            if operation=='create':
                if contact is not None or revision!=0 or set(data)-{'name','email','phone','origin','responsible_ref','notes','duplicate_review'}: raise CRMError('INVALID_CREATE')
                values=self.normalized(data)
                self.duplicates(values,None,data.get('duplicate_review'))
                item={**values,'id':str(uuid.uuid4()),'revision':1,'status':'PROSPECT','consents':{},'tasks':[],
                      'duplicate_review':data.get('duplicate_review'),'customer_ref':None,'stage':'nuevo'}
            else:
                if not isinstance(contact,str) or len(contact)>96: raise CRMError('INVALID_CONTACT_ID')
                current=self.store.get(contact)
                if current is None: raise CRMError('CONTACT_NOT_FOUND',404)
                if current['revision']!=revision: raise CRMError('REVISION_CONFLICT',409)
                original=json.loads(json.dumps(current))
                item=json.loads(json.dumps(current))
                if operation=='update':
                    if not data or set(data)-{'name','email','phone','origin','responsible_ref','notes','duplicate_review','stage'}: raise CRMError('INVALID_UPDATE')
                    values=self.normalized(data,current)
                    self.duplicates(values,contact,data.get('duplicate_review'))
                    if values['email']!=current['email'] or values['phone']!=current['phone']:
                        for consent in item['consents'].values(): consent['granted']=False
                    item.update(values)
                    item['duplicate_review']=data.get('duplicate_review')
                    if 'stage' in data:
                        if data['stage'] not in ('nuevo','contactado','propuesta','ganado','cerrado'): raise CRMError('INVALID_STAGE')
                        item['stage']=data['stage']
                elif operation=='convert':
                    if data or item['status']!='PROSPECT': raise CRMError('INVALID_CONVERSION')
                    item['status']='CUSTOMER';item['stage']='ganado'
                elif operation=='withdraw':
                    if set(data)!={'reason'}: raise CRMError('INVALID_WITHDRAWAL')
                    text(data['reason'],500);item['status']='WITHDRAWN';item['stage']='cerrado'
                    for consent in item['consents'].values(): consent['granted']=False
                elif operation=='consent':
                    if set(data)!={'channel','purpose','granted','evidence_digest','expires_at'}: raise CRMError('INVALID_CONSENT')
                    if data['channel'] not in ('EMAIL','SMS','MMS','WHATSAPP','META_DM','PUBLIC_COMMENT','YOUTUBE_COMMENT','TIKTOK_DM') or data['purpose'] not in ('MARKETING','SERVICE','CROSS_SYSTEM_ATTRIBUTION') or type(data['granted'])!=bool or not isinstance(data['evidence_digest'],str) or not re.fullmatch('[a-f0-9]{64}',data['evidence_digest']): raise CRMError('INVALID_CONSENT')
                    expires=moment(data['expires_at']);now=datetime.now(timezone.utc)
                    if data['granted'] and not now<expires<=now+timedelta(days=366): raise CRMError('INVALID_CONSENT_EXPIRY')
                    if item['status']=='WITHDRAWN' and data['granted']: raise CRMError('CONTACT_WITHDRAWN',409)
                    item['consents'][data['channel']+':'+data['purpose']]={**data,'recorded_at':now.isoformat(),'recorded_by':self.actor,'delivery_authorized':False,'evidence_authenticity_verified':False}
                elif operation=='task':
                    if set(data)!={'title','due_at','responsible_ref'} or len(item['tasks'])>=100: raise CRMError('INVALID_TASK')
                    if not self.member(data['responsible_ref']): raise CRMError('RESPONSIBLE_NOT_IN_COMPANY',403)
                    item['tasks'].append({'id':request_id,'title':text(data['title'],200),'due_at':moment(data['due_at']).isoformat(),'responsible_ref':data['responsible_ref'],'completed':False})
                elif operation=='complete_task':
                    if set(data)!={'task_id'}: raise CRMError('INVALID_TASK')
                    task=next((t for t in item['tasks'] if t['id']==data['task_id']),None)
                    if task is None: raise CRMError('TASK_NOT_FOUND',404)
                    task['completed']=True
                else: raise CRMError('UNKNOWN_OPERATION')
                item['revision']+=1
            self.store.save(item,revision)
            receipt={'contact_id':item['id'],'revision':item['revision'],'status':item['status'],'customer_ref':item['customer_ref'],'replayed':False}
            audit_data={'submitted':data,'previous_revision':revision}
            if original is not None and revision==0:audit_data['adopted_record']=original
            self.store.append(request_id,self.actor,operation,item['id'],fingerprint,receipt,audit_data)
        return receipt
