"""Owner-reviewed commercial sale; accepted quote is intent, never money by itself."""
import copy,uuid,re
from datetime import datetime,timezone,timedelta,date
from .crm import CRMError,text,digest,moment
from .opportunities import uuid_ref
class Sales:
    def __init__(self,store,quotes,ledger,operations):self.store,self.quotes,self.ledger,self.operations,self.actor=store,quotes,ledger,operations,quotes.actor
    def authority(self):return self.quotes.authority(True)
    def get(self,ref):
        self.authority();uuid_ref(ref);row=self.store.get(ref)
        if not row:raise CRMError('SALE_NOT_FOUND',404)
        event=self.store.last_event(ref)
        if not event or event['event_digest']!=row['last_event_digest'] or digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest'] or event['result_digest']!=digest({k:v for k,v in row.items() if k!='last_event_digest'}):raise CRMError('SALE_INTEGRITY_REVIEW_REQUIRED',503)
        return row
    def source(self,ref):
        quote=self.quotes.get(ref);self.quotes.history(ref)
        a=quote.get('acceptance')
        if quote['status']!='ACCEPTED' or not a or a['content_digest']!=quote['content_digest'] or a['version']!=quote['version'] or moment(a['accepted_at'])>=moment(quote['content']['expires_at']):raise CRMError('ACCEPTED_QUOTE_REQUIRED',409)
        if self.quotes.crm.get(quote['content']['contact_id'])['status']=='WITHDRAWN':raise CRMError('CONTACT_WITHDRAWN',409)
        return {'quotation_id':quote['id'],'version':quote['version'],'content_digest':quote['content_digest'],'content':copy.deepcopy(quote['content']),'acceptance':copy.deepcopy(a)}
    def list(self,q='',offset=0,limit=30):
        self.authority()
        if not isinstance(q,str) or len(q)>200 or type(offset)!=int or not 0<=offset<=100000 or type(limit)!=int or not 1<=limit<=100:raise CRMError('INVALID_PAGE')
        rows,more=self.store.list(q,'',offset,limit)
        for row in rows:self.get(row['id'])
        return {'sales':[{k:row.get(k) for k in ('id','title','status','revision','quotation_id','journal','reversal','ledger_written','fiscal_document_issued','money_transferred')} for row in rows],'next_offset':offset+limit if more else None}
    def history(self,ref,offset=0):
        if type(offset)!=int or not 0<=offset<=100000:raise CRMError('INVALID_PAGE')
        row=self.get(ref);previous='0'*64;events=[]
        for event in self.store.events(ref):
            if event['previous_event_digest']!=previous or digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest']:raise CRMError('SALE_HISTORY_REVIEW_REQUIRED',503)
            previous=event['event_digest'];events.append(event)
        if previous!=row['last_event_digest']:raise CRMError('SALE_HISTORY_REVIEW_REQUIRED',503)
        return {'events':events[offset:offset+2],'next_offset':offset+2 if len(events)>offset+2 else None,'history_verified':True}
    def receipt(self,rid):
        self.authority();uuid_ref(rid);event=self.store.event(rid)
        if not event or event['scope']!=self.store.scope or event['actor']!=self.actor:raise CRMError('SALE_RECEIPT_NOT_FOUND',404)
        if digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest']:raise CRMError('SALE_INTEGRITY_REVIEW_REQUIRED',503)
        return event['receipt']
    def validate_review(self,data):
        if set(data)!={'economic_fact','entry_date','accounts','operation','documents','support_digest','confirmed'} or data['confirmed'] is not True:raise CRMError('SALE_REVIEW_FIELDS_REQUIRED')
        if data['economic_fact'] not in ('UNCONDITIONAL_RECEIVABLE','SERVICE_DELIVERED'):raise CRMError('INVALID_ECONOMIC_FACT')
        try:day=date.fromisoformat(data['entry_date'])
        except (ValueError,TypeError):raise CRMError('INVALID_ENTRY_DATE') from None
        if day>datetime.now(timezone.utc).date():raise CRMError('FUTURE_SALE_ACCOUNTING_NOT_ALLOWED')
        if not isinstance(data['support_digest'],str) or not re.fullmatch('[a-f0-9]{64}',data['support_digest']):raise CRMError('SALE_SUPPORT_REQUIRED')
        documents=data['documents']
        if not isinstance(documents,list) or not 1<=len(documents)<=10:raise CRMError('SALE_DOCUMENT_REFERENCES_REQUIRED')
        for doc in documents:
            if not isinstance(doc,dict) or set(doc)!={'kind','reference','sha256'} or doc['kind'] not in ('CONTRACT','DELIVERY_SUPPORT','FISCAL_REFERENCE','OTHER_SUPPORT') or not isinstance(doc['sha256'],str) or not re.fullmatch('[a-f0-9]{64}',doc['sha256']):raise CRMError('INVALID_SALE_DOCUMENT_REFERENCE')
            text(doc['reference'],200)
    def review(self,item,data):
        self.validate_review(data)
        source=self.source(item['quotation_id'])
        if source['content_digest']!=item['source']['content_digest']:raise CRMError('SALE_SOURCE_CHANGED',409)
        plan=self.ledger.preview(source,data);operation=self.operations.validate(source,data['operation'],data['economic_fact'])
        return {'terms':copy.deepcopy(data),'preview':plan,'operation_check':operation,'actor_ref':self.actor,'reviewed_at':datetime.now(timezone.utc).isoformat(),'expires_at':(datetime.now(timezone.utc)+timedelta(minutes=15)).isoformat(),'source_digest':digest(source)}
    def event(self,item,rid,operation,data,fingerprint,revision):
        item['revision']=revision+1;item['updated_at']=datetime.now(timezone.utc).isoformat();receipt={k:item.get(k) for k in ('id','status','revision','quotation_id','journal','reversal','ledger_written','fiscal_document_issued','money_transferred')};receipt['sale_id']=item['id'];receipt['replayed']=False
        event={'id':rid,'scope':self.store.scope,'actor':self.actor,'item_id':item['id'],'operation':operation,'fingerprint':fingerprint,'previous_event_digest':item.get('last_event_digest','0'*64),'result_digest':digest({k:v for k,v in item.items() if k!='last_event_digest'}),'data':data,'snapshot':copy.deepcopy({k:v for k,v in item.items() if k!='last_event_digest'}),'receipt':receipt}
        event['event_digest']=digest(event);item['last_event_digest']=event['event_digest'];self.store.save(item,revision);self.store.append(event);return receipt
    def command(self,body):
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','sale_id','expected_revision','data'} or not isinstance(body['data'],dict):raise CRMError('INVALID_COMMAND')
        rid=uuid_ref(body['request_id']);ref=body['sale_id'];op=body['operation'];rev=body['expected_revision'];data=body['data']
        if type(rev)!=int or not 0<=rev<2**31:raise CRMError('INVALID_REVISION')
        signature=digest({'scope':self.store.scope,'actor':self.actor,'body':body})
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature:raise CRMError('REQUEST_CONFLICT',409)
                return self.receipt(rid)|{'replayed':True}
            if op=='create':
                if ref is not None or rev or set(data)!={'quotation_id'}:raise CRMError('INVALID_SALE_FIELDS')
                source=self.source(data['quotation_id']);code='SALE:'+source['quotation_id']
                if self.store.find_code(code):raise CRMError('QUOTATION_ALREADY_HAS_SALE',409)
                item={'id':str(uuid.uuid4()),'code':code,'title':source['content']['title'],'quotation_id':source['quotation_id'],'source':source,'status':'DRAFT','review':None,'operation_refs':[],'journal':None,'reversal':None,'ledger_written':False,'fiscal_document_issued':False,'money_transferred':False}
            else:
                item=copy.deepcopy(self.get(ref));self.history(ref)
                if item['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
                if op=='review':
                    if item['status'] not in ('DRAFT','REVIEWED','CANCELLED') or item.get('journal'):raise CRMError('INVALID_SALE_TRANSITION',409)
                    item['review']=self.review(item,data);item['status']='REVIEWED'
                elif op=='confirm':
                    if data!={'confirmed':True} or item['status']!='REVIEWED':raise CRMError('SECOND_SALE_CONFIRMATION_REQUIRED',409)
                    review=item['review']
                    if review['actor_ref']!=self.actor or datetime.now(timezone.utc)>=moment(review['expires_at']):raise CRMError('SALE_REVIEW_EXPIRED_OR_FOREIGN',409)
                    current=self.review(item,review['terms'])
                    if current['preview']!=review['preview'] or current['source_digest']!=review['source_digest'] or current['operation_check']!=review['operation_check']:raise CRMError('SALE_PRECONDITIONS_CHANGED',409)
                    item['operation_refs']=self.operations.reserve(item)
                    item['journal']=self.ledger.post(item);item['ledger_written']=True;item['status']='CONFIRMED';self.store.outbox(item,'CONFIRMED')
                elif op=='review_reversal':
                    if item['status']!='CONFIRMED' or set(data)!={'reason','support_digest','confirmed'} or data['confirmed'] is not True:raise CRMError('INVALID_SALE_REVERSAL')
                    text(data['reason'],500)
                    if not isinstance(data['support_digest'],str) or not re.fullmatch('[a-f0-9]{64}',data['support_digest']):raise CRMError('SALE_SUPPORT_REQUIRED')
                    self.store.ensure_no_live_payment(item)
                    self.ledger.verify(item);item['reversal_review']={**data,'actor_ref':self.actor,'expires_at':(datetime.now(timezone.utc)+timedelta(minutes=15)).isoformat()};item['status']='REVERSAL_REVIEWED'
                elif op=='reverse':
                    if item['status']!='REVERSAL_REVIEWED' or data!={'confirmed':True}:raise CRMError('SECOND_REVERSAL_CONFIRMATION_REQUIRED')
                    review=item['reversal_review']
                    if review['actor_ref']!=self.actor or datetime.now(timezone.utc)>=moment(review['expires_at']):raise CRMError('SALE_REVIEW_EXPIRED_OR_FOREIGN',409)
                    item['reversal']=self.ledger.reverse(item);self.operations.release(item);item['status']='REVERSED';self.store.outbox(item,'REVERSED')
                elif op=='cancel':
                    if item['status'] not in ('DRAFT','REVIEWED') or set(data)!={'reason'}:raise CRMError('INVALID_SALE_TRANSITION',409)
                    item['cancel_reason']=text(data['reason'],500);item['status']='CANCELLED'
                else:raise CRMError('UNKNOWN_OPERATION')
            return self.event(item,rid,op,data,signature,rev)
