"""Durable source-side accounting saga. Unknown remote outcome never releases a live claim."""
import copy,uuid
from datetime import datetime,timezone,timedelta
from .sales import Sales
from .crm import CRMError,digest,moment,text
from .opportunities import uuid_ref
class SalesSaga(Sales):
    def __init__(self,store,quotes,operations,bridge):super().__init__(store,quotes,None,operations);self.bridge=bridge
    def native_command(self,op,sale,request_id,data=None,revision=None):
        return {'request_id':request_id,'operation':op,'sale_id':sale.get('native_sale_id'),'expected_revision':sale.get('native_revision',0) if revision is None else revision,'data':data or {}}
    def external(self,item,command,proof):
        return self.bridge.rpc('command',{'source':item['source'],'command':command,'operation_proof':{k:v for k,v in proof.items() if k!='plans'}},item['provider_ref'])
    def preview(self,item,data,rid):
        self.validate_review(data)
        # Validate the local source and operational inputs before any peer writes.
        current=self.source(item['quotation_id'])
        if current['content_digest']!=item['source']['content_digest']:raise CRMError('SALE_SOURCE_CHANGED',409)
        proof=self.operations.validate(current,data['operation'],data['economic_fact'])
        if not item.get('native_sale_id'):
            create=self.native_command('create',item,str(uuid.uuid5(uuid.NAMESPACE_URL,'sale-source-create:'+item['id'])),{'quotation_id':item['quotation_id']},0);created=self.external(item,create,proof);item['native_sale_id']=created['sale']['id'];item['native_revision']=created['sale']['revision'];item['binding_id']=created['binding_id']
        command=self.native_command('review',item,str(uuid.uuid5(uuid.NAMESPACE_URL,'sale-source-review:'+rid)),data);result=self.external(item,command,proof);remote=result['sale']
        if remote['status']!='REVIEWED' or result['binding_id']!=item['binding_id']:raise CRMError('SALE_LEDGER_CONTEXT_MISMATCH',503)
        item['native_revision']=remote['revision'];return {'terms':copy.deepcopy(data),'preview':remote['review']['preview'],'actor_ref':self.actor,'expires_at':remote['review']['expires_at'],'operation_plan_digest':proof['plan_digest'],'remote_actor_ref':remote['review']['actor_ref']}
    def state(self,item):
        response=self.bridge.rpc('state',{'sale_id':item['native_sale_id']},item['provider_ref']);remote=response.get('sale')
        if not isinstance(remote,dict) or response.get('binding_id')!=item['binding_id'] or remote['id']!=item['native_sale_id'] or remote['source']['content_digest']!=item['source']['content_digest']:raise CRMError('SALE_LEDGER_CONTEXT_MISMATCH',503)
        if item.get('review') and remote['journal'] and remote['review']['preview']!=item['review']['preview']:raise CRMError('SALE_LEDGER_CONTEXT_MISMATCH',503)
        return remote
    def apply(self,ref,remote,pending_id):
        with self.store.transaction():
            self.authority();self.store.lock();item=copy.deepcopy(self.get(ref));revision=item['revision']
            if (item.get('pending') or {}).get('request_id')!=pending_id:raise CRMError('SALE_PENDING_INTENT_CHANGED',409)
            if remote['status'] in ('CONFIRMED','REVERSAL_REVIEWED','REVERSED'):
                journal=remote.get('journal')
                if not journal or journal.get('posted') is not True or journal.get('company_id')!=item['review']['preview']['company_id']:raise CRMError('SALE_LEDGER_CONTEXT_MISMATCH',503)
                item.update(journal=journal,ledger_written=True,native_revision=remote['revision'])
                if remote['status']=='REVERSED':
                    if not remote.get('reversal') or remote['reversal'].get('posted') is not True:raise CRMError('SALE_LEDGER_CONTEXT_MISMATCH',503)
                    item['reversal']=remote['reversal'];self.operations.release(item);item['status']='REVERSED'
                else:self.operations.confirm(item);item['status']='CONFIRMED'
            elif remote['status']=='CANCELLED':self.operations.release(item);item['status']='CANCELLED';item['native_revision']=remote['revision']
            else:return self.summary(item)
            item['pending']=None;nonce=str(uuid.uuid5(uuid.NAMESPACE_URL,'sale-source-ack:'+pending_id));self.event(item,nonce,'ledger_acknowledged',{'native_status':remote['status']},digest(remote),revision);return self.summary(item)
    def summary(self,item):return {**{k:item.get(k) for k in ('id','status','revision','quotation_id','journal','reversal','ledger_written','fiscal_document_issued','money_transferred')},'sale_id':item['id'],'cross_database_atomic':False,'replayed':False}
    def recover(self,item):
        if not item.get('pending'):return self.summary(item)
        original=item['pending']['request_id'];remote=self.state(item)
        if remote['status'] in ('CONFIRMED','REVERSED','CANCELLED'):return self.apply(item['id'],remote,original)
        phase=item['pending']['phase']
        if phase in ('CONFIRM','REVERSE'):
            if phase=='CONFIRM':proof=self.operations.validate(self.source(item['quotation_id']),item['review']['terms']['operation'],item['review']['terms']['economic_fact'],item['operation_refs'])
            else:proof={'plan_digest':item['review']['operation_plan_digest'],'valid':True,'operation_refs':item['operation_refs'],'reserved':True,'requires_capacity':bool(item['operation_refs'])}
            command=self.native_command('confirm' if phase=='CONFIRM' else 'reverse',item,item['pending']['native_request_id'],{'confirmed':True},item['pending']['native_revision']);result=self.external(item,command,proof);return self.apply(item['id'],result['sale'],original)
        return self.summary(item)
    def receipt(self,rid):
        receipt=super().receipt(rid);item=self.get(receipt['sale_id']);return self.summary(item)|{'replayed':True}
    def command(self,body):
        self.authority()
        if not isinstance(body,dict) or set(body)!={'request_id','operation','sale_id','expected_revision','data'} or not isinstance(body['data'],dict):raise CRMError('INVALID_COMMAND')
        rid=uuid_ref(body['request_id']);op=body['operation'];ref=body['sale_id'];rev=body['expected_revision'];data=body['data']
        if type(rev)!=int or not 0<=rev<2**31:raise CRMError('INVALID_REVISION')
        if op=='create':
            if ref is not None or rev or set(data)!={'quotation_id','provider_id'}:raise CRMError('INVALID_SALE_FIELDS')
            uuid_ref(data['provider_id']);signature=digest({'scope':self.store.scope,'actor':self.actor,'body':body})
            with self.store.transaction():
                self.authority();self.store.lock();prior=self.store.event(rid)
                if prior:
                    if prior['fingerprint']!=signature:raise CRMError('REQUEST_CONFLICT',409)
                    return self.receipt(rid)
                source=self.source(data['quotation_id']);code='SALE:'+source['quotation_id']
                if self.store.find_code(code):raise CRMError('QUOTATION_ALREADY_HAS_SALE',409)
                item={'id':str(uuid.uuid4()),'code':code,'title':source['content']['title'],'quotation_id':source['quotation_id'],'provider_ref':data['provider_id'],'source':source,'status':'DRAFT','review':None,'operation_refs':[],'journal':None,'reversal':None,'ledger_written':False,'fiscal_document_issued':False,'money_transferred':False,'pending':None}
                self.event(item,rid,op,data,signature,0)
            return self.summary(item)
        signature=digest({'scope':self.store.scope,'actor':self.actor,'body':body})
        with self.store.transaction():
            self.authority();self.store.lock();prior=self.store.event(rid)
            if prior:
                if prior['fingerprint']!=signature:raise CRMError('REQUEST_CONFLICT',409)
                return self.receipt(rid)
            item=copy.deepcopy(self.get(ref))
            if item['revision']!=rev:raise CRMError('REVISION_CONFLICT',409)
            self.history(ref)
            if op=='review':
                if item['status'] not in ('DRAFT','REVIEWED','CANCELLED') or item.get('journal'):raise CRMError('INVALID_SALE_TRANSITION',409)
                item['operation_refs']=[];item['pending']=None
                item['review']=self.preview(item,data,rid);item['status']='REVIEWED'
            elif op in ('confirm','reverse'):
                expected='REVIEWED' if op=='confirm' else 'REVERSAL_REVIEWED';review=item.get('review' if op=='confirm' else 'reversal_review')
                if data!={'confirmed':True} or item['status']!=expected or not review or review['actor_ref']!=self.actor or datetime.now(timezone.utc)>=moment(review['expires_at']):raise CRMError('SALE_REVIEW_EXPIRED_OR_FOREIGN',409)
                if op=='confirm':item['operation_refs']=self.operations.reserve(item)
                item['pending']={'request_id':rid,'native_request_id':str(uuid.uuid5(uuid.NAMESPACE_URL,'sale-source-'+op+':'+rid)),'native_revision':item['native_revision'],'phase':'CONFIRM' if op=='confirm' else 'REVERSE'};item['status']='LEDGER_PENDING' if op=='confirm' else 'REVERSAL_PENDING'
            elif op=='review_reversal':
                self.store.ensure_no_live_payment(item)
                if item['status']!='CONFIRMED' or set(data)!={'reason','support_digest','confirmed'} or data['confirmed'] is not True:raise CRMError('INVALID_SALE_REVERSAL')
                proof={'plan_digest':item['review']['operation_plan_digest'],'valid':True,'operation_refs':item['operation_refs'],'reserved':True,'requires_capacity':bool(item['operation_refs'])};cmd=self.native_command('review_reversal',item,str(uuid.uuid5(uuid.NAMESPACE_URL,'sale-source-reversal-review:'+rid)),data);result=self.external(item,cmd,proof);remote=result['sale'];item['native_revision']=remote['revision'];item['reversal_review']={**data,'actor_ref':self.actor,'expires_at':remote['reversal_review']['expires_at']};item['status']='REVERSAL_REVIEWED'
            elif op=='recover':
                if data!={} or item['status'] not in ('LEDGER_PENDING','REVERSAL_PENDING'):raise CRMError('SALE_PENDING_REQUIRED',409)
                # Recovery uses the persisted original native request, not this command's UUID.
                pass
            elif op=='cancel':
                if set(data)!={'reason'} or item['status'] not in ('DRAFT','REVIEWED','LEDGER_PENDING'):raise CRMError('INVALID_SALE_TRANSITION',409)
                text(data['reason'],500)
                if item.get('native_sale_id'):
                    remote=self.state(item)
                    if remote['status'] in ('CONFIRMED','REVERSED'):
                        raise CRMError('SALE_ALREADY_POSTED_RECOVER_REQUIRED',409)
                    proof={'plan_digest':(item.get('review') or {}).get('operation_plan_digest','0'*64),'valid':True,'operation_refs':item['operation_refs'],'reserved':bool(item['operation_refs']),'requires_capacity':bool(item['operation_refs'])};cmd=self.native_command('cancel',item,str(uuid.uuid5(uuid.NAMESPACE_URL,'sale-source-cancel:'+rid)),data,remote['revision']);result=({'sale':remote} if remote['status']=='CANCELLED' else self.external(item,cmd,proof))
                    if result['sale']['status']!='CANCELLED':raise CRMError('SALE_LEDGER_RESULT_UNCERTAIN',503)
                    item['native_revision']=result['sale']['revision']
                self.operations.release(item);item['status']='CANCELLED';item['pending']=None
            else:raise CRMError('UNKNOWN_OPERATION')
            self.event(item,rid,op,data,signature,rev)
        if op in ('confirm','reverse','recover'):
            try:return self.recover(self.get(ref))
            except CRMError as exc:
                if exc.status not in (409,503):raise
                result=self.summary(self.get(ref));result['recovery_required']=True;result['error_code']=str(exc);return result
        return self.summary(self.get(ref))
