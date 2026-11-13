"""Durable checkout intentions. Unknown transmission cannot be retried as a new charge.
Authenticated Bold confirmation/settlement stays blocked until its real contract
is qualified; a browser return, declared hash or link never marks money received.
"""
import copy,uuid,json,os,re
from datetime import datetime,timezone
from .sales import Sales
from .crm import CRMError,digest,text
from .opportunities import uuid_ref
from .bold_gateway import BoldGateway,GatewayError,amount

def runtime_gateway(scope):
    try:profiles=json.loads(os.environ.get('COMMERCIAL_BOLD_MERCHANTS','{}'))
    except (ValueError,TypeError):raise CRMError('BOLD_SCOPED_CONFIGURATION_REQUIRED',503) from None
    p=profiles.get(scope) if isinstance(profiles,dict) else None
    if not isinstance(p,dict) or set(p)!={'enabled','environment','merchant_ref','identity_env','secret_env','contract_digest'} or p['enabled'] is not True or p['environment']!='SANDBOX':raise CRMError('BOLD_SCOPED_CONFIGURATION_REQUIRED',503)
    if not isinstance(p['merchant_ref'],str) or not re.fullmatch('[A-Za-z0-9_-]{1,100}',p['merchant_ref']) or not isinstance(p['contract_digest'],str) or not re.fullmatch('[a-f0-9]{64}',p['contract_digest']):raise CRMError('BOLD_MERCHANT_REVIEW_REQUIRED',503)
    for name in ('identity_env','secret_env'):
        if not isinstance(p[name],str) or not re.fullmatch('BOLD_[A-Z0-9_]{1,95}',p[name]):raise CRMError('BOLD_SECRET_BINDING_REQUIRED',503)
    if p['identity_env']==p['secret_env']:raise CRMError('BOLD_DISTINCT_SECRET_BINDINGS_REQUIRED',503)
    gateway=BoldGateway(os.environ.get(p['identity_env'],''),os.environ.get(p['secret_env'],''));gateway.merchant_ref=p['merchant_ref'];gateway.profile_digest=digest(p);return gateway

class Payments(Sales):
    def __init__(self,store,sales,gateway=None):
        self.store,self.sales,self.actor,self.quotes=store,sales,sales.actor,sales.quotes
        self.ledger=None;self.gateway_factory=gateway or (lambda:runtime_gateway(store.scope))
    def authority(self):return self.sales.authority()
    def sale(self,ref):
        sale=self.sales.get(uuid_ref(ref))
        if sale['status']!='CONFIRMED' or sale.get('ledger_written') is not True or not sale.get('journal'):raise CRMError('CONFIRMED_LEDGER_SALE_REQUIRED',409)
        if self.sales.ledger is not None:
            if sale['source'].get('_external'):raise CRMError('SOURCE_PAYMENT_WORKFLOW_REQUIRED',409)
            self.sales.ledger.verify(sale)
        return sale
    def get(self,ref):return super().get(ref)
    def summary(self,row):return {k:row.get(k) for k in ('id','payment_id','sale_id','reference','amount','currency','status','revision','checkout_url','provider_link_id','payment_verified','ledger_written','money_transferred','error_code')}
    def list(self,q='',offset=0,limit=30):
        self.authority()
        if not isinstance(q,str) or len(q)>200 or type(offset)!=int or not 0<=offset<=100000 or type(limit)!=int or not 1<=limit<=100:raise CRMError('INVALID_PAGE')
        rows,more=self.store.list(q,'',offset,limit)
        for row in rows:self.get(row['id'])
        return {'payments':[self.summary(row) for row in rows],'next_offset':offset+limit if more else None}
    def receipt(self,rid):
        self.authority();uuid_ref(rid);event=self.store.event(rid)
        if not event or event['scope']!=self.store.scope or event['actor']!=self.actor:raise CRMError('PAYMENT_RECEIPT_NOT_FOUND',404)
        if digest({k:v for k,v in event.items() if k!='event_digest'})!=event['event_digest']:raise CRMError('PAYMENT_INTEGRITY_REVIEW_REQUIRED',503)
        return self.summary(self.get(event['item_id']))|{'replayed':True}
    def record(self,item,rid,op,data,fingerprint,revision):
        item['revision']=revision+1;item['updated_at']=datetime.now(timezone.utc).isoformat()
        snapshot=copy.deepcopy({k:v for k,v in item.items() if k!='last_event_digest'})
        event={'id':rid,'scope':self.store.scope,'actor':self.actor,'item_id':item['id'],'operation':op,'fingerprint':fingerprint,'previous_event_digest':item.get('last_event_digest','0'*64),'result_digest':digest(snapshot),'snapshot':snapshot,'data':data,'receipt':self.summary(item)}
        event['event_digest']=digest(event);item['last_event_digest']=event['event_digest'];self.store.save(item,revision);self.store.append(event);return self.summary(item)
    def command(self,body):
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','payment_id','expected_revision','data'} or not isinstance(body['data'],dict):raise CRMError('INVALID_PAYMENT_COMMAND')
        rid=uuid_ref(body['request_id']);op=body['operation'];ref=body['payment_id'];rev=body['expected_revision'];data=body['data']
        if type(rev)!=int or not 0<=rev<2**31:raise CRMError('INVALID_REVISION')
        signature=digest({'scope':self.store.scope,'actor':self.actor,'body':body});dispatch=False
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature:raise CRMError('REQUEST_CONFLICT',409)
                return self.receipt(rid)
            if op=='create':
                if ref is not None or rev!=0 or set(data)!={'sale_id','confirmed'} or data['confirmed'] is not True:raise CRMError('PAYMENT_CREATION_REVIEW_REQUIRED')
                sale=self.sale(data['sale_id']);code='PAY:'+sale['id']
                if self.store.find_code(code):raise CRMError('SALE_ALREADY_HAS_PAYMENT_INTENT',409)
                ref=str(uuid.uuid4());estimate=sale['source']['content']['estimate']
                try:total=amount(estimate['total'])
                except GatewayError:raise CRMError('PAYMENT_AMOUNT_NOT_QUALIFIED',409) from None
                if estimate['currency']!='COP':raise CRMError('PAYMENT_CURRENCY_NOT_QUALIFIED',409)
                item={'id':ref,'payment_id':ref,'code':code,'title':sale['title'],'sale_id':sale['id'],'source_digest':sale['source']['content_digest'],'source_journal':copy.deepcopy(sale['journal']),'reference':'PAY-'+ref.replace('-',''),'amount':total,'currency':'COP','status':'DRAFT','checkout_url':None,'provider_link_id':None,'payment_verified':False,'ledger_written':False,'money_transferred':False,'error_code':None,'pending_request':None}
            else:
                item=copy.deepcopy(self.get(uuid_ref(ref)));self.history(ref)
                if item['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
                if op=='checkout':
                    if set(data)!={'confirmed'} or data['confirmed'] is not True or item['status'] not in ('DRAFT','BLOCKED'):raise CRMError('CHECKOUT_REVIEW_OR_RECONCILIATION_REQUIRED',409)
                    sale=self.sale(item['sale_id'])
                    if sale['journal']!=item['source_journal'] or sale['source']['content_digest']!=item['source_digest']:raise CRMError('PAYMENT_SOURCE_CHANGED',409)
                    try:gateway=self.gateway_factory()
                    except (CRMError,GatewayError) as exc:item.update(status='BLOCKED',error_code=str(exc))
                    else:
                        item.update(status='DISPATCHING',pending_request=rid,error_code=None,merchant_ref=getattr(gateway,'merchant_ref',None),profile_digest=getattr(gateway,'profile_digest',None));dispatch=True
                elif op=='recover':
                    if data or item['status'] not in ('DISPATCHING','UNKNOWN','CHECKOUT_READY'):raise CRMError('PAYMENT_RECONCILIATION_REQUIRED',409)
                    # Read-only recovery never resends a POST. An authenticated
                    # provider query/webhook is required to resolve uncertainty.
                    item['error_code']='BOLD_AUTHENTIC_RECONCILIATION_REQUIRED'
                    if item['status']=='DISPATCHING':item['status']='UNKNOWN'
                elif op=='cancel':
                    if set(data)!={'reason'} or item['status'] not in ('DRAFT','BLOCKED'):raise CRMError('PROVIDER_CANCELLATION_VERIFICATION_REQUIRED',409)
                    item['cancel_reason']=text(data['reason'],500);item['status']='CANCELLED'
                else:raise CRMError('UNSUPPORTED_PAYMENT_OPERATION')
            result=self.record(item,rid,op,data,signature,rev)
        if not dispatch:return result
        # The transmission intent has committed before doing network I/O.
        try:result=gateway.create(item['reference'],item['amount'],item['currency'],item['title']);status='CHECKOUT_READY';error=None
        except (GatewayError,CRMError) as exc:
            result={};status='UNKNOWN' if getattr(exc,'uncertain',False) else 'BLOCKED';error=str(exc)
        with self.store.transaction():
            self.authority();self.store.lock();current=copy.deepcopy(self.get(ref))
            if current['pending_request']!=rid or current['status'] not in ('DISPATCHING','UNKNOWN'):raise CRMError('PAYMENT_INTENT_CHANGED',409)
            revision=current['revision'];current.update(status=status,error_code=error)
            if status=='CHECKOUT_READY':current.update(checkout_url=result['checkout_url'],provider_link_id=result['provider_link_id'])
            nonce=str(uuid.uuid5(uuid.NAMESPACE_URL,'payment-result:'+rid));return self.record(current,nonce,'checkout_result',{'result_status':status},digest({'request':rid,'result':result,'error':error}),revision)
    def browser_return(self,*args,**kwargs):raise CRMError('BROWSER_RETURN_IS_NOT_PAYMENT_PROOF',409)
    def confirm(self,*args,**kwargs):raise CRMError('BOLD_AUTHENTIC_CONFIRMATION_REQUIRED',503)
