"""Owned marketing asset library; originals never cross the anonymous publication boundary."""
import json,uuid,hashlib,copy
from datetime import datetime,timezone
from .crm import CRMError,text,digest,moment
from .opportunities import uuid_ref
from .library_sanitize import sanitize,MAX_UPLOAD,MAX_DELIVERY
TEMPLATES={'SQUARE':'Cuadrada 1:1','STORY':'Vertical 9:16','LANDSCAPE':'Horizontal 16:9'}
MAX_BYTES=200*1024*1024
MAX_BLOBS=200

def metadata(value):
    if not isinstance(value,dict) or set(value)!={'title','brand','rights','classification'} or value['classification']!='MARKETING':raise CRMError('LIBRARY_MARKETING_CLASSIFICATION_REQUIRED')
    brand=value['brand'];rights=value['rights']
    if not isinstance(brand,dict) or set(brand)!={'name','tagline','template'} or not isinstance(brand['template'],str) or brand['template'] not in TEMPLATES:raise CRMError('INVALID_LIBRARY_BRAND')
    if not isinstance(rights,dict) or set(rights)!={'holder','license','reference','valid_until','public_web'} or rights['license'] not in ('UNCONFIRMED','OWNED','LICENSED') or type(rights['public_web'])!=bool:raise CRMError('INVALID_LIBRARY_RIGHTS')
    expiry=moment(rights['valid_until']).isoformat() if rights['valid_until'] is not None else None
    return {'title':text(value['title'],150),'classification':'MARKETING','brand':{'name':text(brand['name'],120),'tagline':text(brand['tagline'],200,True),'template':brand['template']},'rights':{'holder':text(rights['holder'],200,True),'license':rights['license'],'reference':text(rights['reference'],300,True),'valid_until':expiry,'public_web':rights['public_web']}}

def usable(version):
    rights=version['rights']
    return rights['license'] in ('OWNED','LICENSED') and bool(rights['holder'] and rights['reference']) and rights['public_web'] and (rights['valid_until'] is None or moment(rights['valid_until'])>datetime.now(timezone.utc))
class Library:
    def __init__(self,store,crm):self.store,self.crm,self.actor=store,crm,crm.actor
    def authority(self):
        access=self.crm.authorize()
        if not access.principal['is_manager'] or not access.session()['capability_permissions'].get('media.image.resize'):raise CRMError('LOCAL_MEDIA_ADMINISTRATOR_REQUIRED',403)
    def get(self,ref):
        self.authority();uuid_ref(ref);item=self.store.get(ref)
        if not item:raise CRMError('LIBRARY_ITEM_NOT_FOUND',404)
        events=list(self.store.events(ref));previous='0'*64
        for event in events:
            if not isinstance(event,dict) or event.get('previous_event_digest')!=previous or event.get('event_digest')!=digest({k:v for k,v in event.items() if k!='event_digest'}):raise CRMError('LIBRARY_HISTORY_REVIEW_REQUIRED',503)
            previous=event['event_digest']
        if not events or len(events)!=item['revision'] or previous!=item['last_event_digest'] or events[-1]['result_digest']!=digest({k:v for k,v in item.items() if k!='last_event_digest'}):raise CRMError('LIBRARY_INTEGRITY_REVIEW_REQUIRED',503)
        return item
    def list(self,offset=0):
        self.authority()
        if type(offset)!=int or not 0<=offset<=100000:raise CRMError('INVALID_PAGE')
        rows,more=self.store.list('','',offset,30)
        for row in rows:self.get(row['id'])
        count,size=self.store.usage()
        return {'items':[{k:x[k] for k in ('id','title','revision','status','published_version')} for x in rows],'next_offset':offset+30 if more else None,'usage':{'originals':count,'bytes':size,'max_originals':MAX_BLOBS,'max_bytes':MAX_BYTES},'templates':TEMPLATES,'adaptation_profiles':__import__(__package__+'.media_adaptation',fromlist=['catalog']).catalog(),'original_publication_allowed':False,'fiscal_vault_connected':False}
    def receipt(self,rid):
        self.authority();uuid_ref(rid);event=self.store.event(rid)
        if not event or event.get('scope')!=self.store.scope or event.get('provider_ref')!=getattr(self.store,'provider',None) or event.get('actor')!=self.actor:raise CRMError('RECEIPT_NOT_FOUND',404)
        if event['event_digest']!=digest({k:v for k,v in event.items() if k!='event_digest'}):raise CRMError('LIBRARY_HISTORY_REVIEW_REQUIRED',503)
        return {**event['receipt'],'previous_receipt_only':True}
    def emit(self,item,rid,operation,signature,expected):
        item['revision']+=1;result={'item_id':item['id'],'revision':item['revision'],'content_version':len(item['versions']),'published_version':item['published_version'],'status':item['status'],'replayed':False}
        event={'id':rid,'scope':self.store.scope,'provider_ref':getattr(self.store,'provider',None),'actor':self.actor,'item_id':item['id'],'operation':operation,'fingerprint':signature,'previous_event_digest':item.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in item.items() if k!='last_event_digest'}),'created_at':datetime.now(timezone.utc).isoformat(),'receipt':result};event['event_digest']=digest(event);item['last_event_digest']=event['event_digest'];self.store.save(item,expected);self.store.append(event);return result
    def upload(self,body,raw,mime):
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','item_id','expected_revision','metadata'}:raise CRMError('INVALID_LIBRARY_UPLOAD')
        rid=uuid_ref(body['request_id']);rev=body['expected_revision']
        if type(rev)!=int or not 0<=rev<200:raise CRMError('INVALID_LIBRARY_REVISION')
        value=metadata(body['metadata']);original_sha=hashlib.sha256(raw).hexdigest();signature=digest({'domain':'LIBRARY_UPLOAD','scope':self.store.scope,'provider':getattr(self.store,'provider',None),'actor':self.actor,'body':body,'original_sha':original_sha,'mime':mime})
        # Reject/recover before decoder work; recheck under the company lock before writing.
        if self.store.event(rid):
            if self.store.event(rid).get('fingerprint')!=signature:raise CRMError('LIBRARY_REQUEST_CONFLICT',409)
            return self.receipt(rid)|{'replayed':True}
        if body['item_id'] is not None:
            current=self.get(body['item_id'])
            if current['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
        elif rev!=0:raise CRMError('INVALID_LIBRARY_CREATE')
        data,delivery_mime,info=sanitize(raw,mime);delivery_sha=hashlib.sha256(data).hexdigest()
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature:raise CRMError('LIBRARY_REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            if body['item_id'] is None:item={'id':str(uuid.uuid4()),'code':str(uuid.uuid4()),'title':value['title'],'revision':0,'status':'PRIVATE','versions':[],'approved_digest':None,'published_version':None,'publisher_ref':None,'system':self.crm.store.system}
            else:
                item=copy.deepcopy(self.get(body['item_id']))
                if item['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
            if len(item['versions'])>=20:raise CRMError('LIBRARY_VERSION_LIMIT',409)
            count,size=self.store.usage()
            if count>=MAX_BLOBS or size+len(raw)+len(data)>MAX_BYTES:raise CRMError('LIBRARY_QUOTA_EXCEEDED',413)
            blob=str(uuid.uuid4());self.store.save_blob(blob,raw,data,original_sha,delivery_sha,delivery_mime)
            version={**value,'number':len(item['versions'])+1,'blob_id':blob,'original_sha256':original_sha,'delivery_sha256':delivery_sha,'original_size':len(raw),'delivery_size':len(data),'original_mime':mime,'delivery_mime':delivery_mime,'media':info,'system':self.crm.store.system,'rights_authenticity_verified':False};item['versions'].append(version);item['title']=value['title'];item['approved_digest']=None
            return self.emit(item,rid,'upload',signature,rev)
    def adapt(self,body):
        """Compute outside the company lock, then revalidate and append atomically."""
        from .media_adaptation import adapt,options
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','item_id','expected_revision','data'} or body['operation']!='adapt' or type(body['expected_revision'])!=int or not 0<=body['expected_revision']<2**31:raise CRMError('INVALID_LIBRARY_COMMAND')
        rid=uuid_ref(body['request_id']);ref=uuid_ref(body['item_id']);rev=body['expected_revision'];data=body['data'];options(data)
        signature=digest({'domain':'LIBRARY_COMMAND','scope':self.store.scope,'provider':getattr(self.store,'provider',None),'actor':self.actor,'body':body})
        if self.store.event(rid):
            self.receipt(rid)
            if self.store.event(rid).get('fingerprint')!=signature:raise CRMError('LIBRARY_REQUEST_CONFLICT',409)
            return self.receipt(rid)|{'replayed':True}
        item=self.get(ref);v=item['versions'][-1]
        if item['revision']>=200:raise CRMError('LIBRARY_REVISION_LIMIT',409)
        if v['media']['kind']=='VIDEO' and not self.crm.authorize().session()['capability_permissions'].get('media.video.resize'):raise CRMError('ADAPTATION_VIDEO_PERMISSION_REQUIRED',403)
        if item['revision']!=rev or v['number']!=data['source_version'] or v['delivery_sha256']!=data['source_sha256']:raise CRMError('ADAPTATION_SOURCE_CHANGED',409)
        if len(item['versions'])>=20:raise CRMError('LIBRARY_VERSION_LIMIT',409)
        self.bytes(ref,v['number'],'delivery');raw,_=self.bytes(ref,v['number'],'original');snapshot=digest(v)
        result,mime,info=adapt(raw,v['original_mime'],data);checksum=hashlib.sha256(result).hexdigest()
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                self.receipt(rid)
                if prior['fingerprint']!=signature:raise CRMError('LIBRARY_REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            item=copy.deepcopy(self.get(ref));v=item['versions'][-1]
            if item['revision']!=rev or digest(v)!=snapshot:raise CRMError('ADAPTATION_SOURCE_CHANGED',409)
            self.bytes(ref,v['number'],'delivery');self.bytes(ref,v['number'],'original')
            count,size=self.store.usage()
            if count>=MAX_BLOBS or size+len(raw)+len(result)>MAX_BYTES:raise CRMError('LIBRARY_QUOTA_EXCEEDED',413)
            blob=str(uuid.uuid4());self.store.save_blob(blob,raw,result,v['original_sha256'],checksum,mime)
            version={**copy.deepcopy(v),'number':len(item['versions'])+1,'blob_id':blob,'delivery_sha256':checksum,'delivery_size':len(result),'delivery_mime':mime,'media':info}
            version['brand']['template']='STORY' if info['height']>info['width'] else 'SQUARE' if info['height']==info['width'] else 'LANDSCAPE'
            item['versions'].append(version);item['approved_digest']=None
            return self.emit(item,rid,'adapt',signature,rev)
    def command(self,body):
        if isinstance(body,dict) and body.get("operation")=="adapt":return self.adapt(body)
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','item_id','expected_revision','data'}:raise CRMError('INVALID_LIBRARY_COMMAND')
        rid=uuid_ref(body['request_id']);ref=uuid_ref(body['item_id']);rev=body['expected_revision'];op=body['operation'];data=body['data']
        if type(rev)!=int or not 0<=rev<2**31 or not isinstance(data,dict):raise CRMError('INVALID_LIBRARY_COMMAND')
        signature=digest({'domain':'LIBRARY_COMMAND','scope':self.store.scope,'provider':getattr(self.store,'provider',None),'actor':self.actor,'body':body})
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature:raise CRMError('LIBRARY_REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            item=copy.deepcopy(self.get(ref))
            if item['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
            if rev>=200 and not(op=='withdraw' and item['published_version'] is not None):raise CRMError('LIBRARY_REVISION_LIMIT',409)
            version=item['versions'][-1]
            if op=='revise':
                if len(item['versions'])>=20:raise CRMError('LIBRARY_VERSION_LIMIT',409)
                value=metadata(data);version={**copy.deepcopy(version),**value,'number':len(item['versions'])+1};item['versions'].append(version);item['title']=value['title'];item['approved_digest']=None
            elif op=='approve':
                if data!={'rights_confirmed':True,'privacy_reviewed':True} or any(type(v)!=bool for v in data.values()):raise CRMError('LIBRARY_REVIEW_REQUIRED')
                if not usable(version):raise CRMError('LIBRARY_PUBLIC_RIGHTS_REQUIRED',409)
                self.bytes(ref,version['number'],'delivery');item['approved_digest']=digest(version)
            elif op=='publish':
                if data!={'confirmed':True} or type(data['confirmed'])!=bool:raise CRMError('LIBRARY_PUBLICATION_REQUIRED')
                if not usable(version) or item['approved_digest']!=digest(version):raise CRMError('LIBRARY_APPROVAL_STALE_OR_EXPIRED',409)
                self.bytes(ref,version['number'],'delivery');item['published_version']=version['number'];item['publisher_ref']=self.actor;item['status']='PUBLISHED'
            elif op=='withdraw':
                if data!={'confirmed':True} or type(data['confirmed'])!=bool:raise CRMError('LIBRARY_WITHDRAWAL_REQUIRED')
                item['published_version']=None;item['approved_digest']=None;item['status']='PRIVATE'
            else:raise CRMError('INVALID_LIBRARY_OPERATION')
            return self.emit(item,rid,op,signature,rev)
    def bytes(self,ref,number,kind='delivery',public=False):
        item=self.get(ref)
        if type(number)!=int or not 1<=number<=20 or kind not in ('original','delivery'):raise CRMError('LIBRARY_VERSION_NOT_FOUND',404)
        version=next((v for v in item['versions'] if v['number']==number),None)
        if not version:raise CRMError('LIBRARY_VERSION_NOT_FOUND',404)
        if public and (kind!='delivery' or item['published_version']!=number or not usable(version)):raise CRMError('LIBRARY_PUBLIC_MEDIA_NOT_FOUND',404)
        row=self.store.blob(version['blob_id'])
        if row is None or (kind=='original' and (row['original_sha']!=version['original_sha256'] or hashlib.sha256(row['original']).hexdigest()!=row['original_sha'])) or (kind=='delivery' and (row['delivery_sha']!=version['delivery_sha256'] or hashlib.sha256(row['delivery']).hexdigest()!=row['delivery_sha'] or row['mime']!=version['delivery_mime'])):raise CRMError('LIBRARY_BLOB_INTEGRITY_REVIEW_REQUIRED',503)
        return row[kind],('application/octet-stream' if kind=='original' else row['mime'])
