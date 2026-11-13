from django.db import connection
from .crm import CRMError,digest
from .state_integrity import verify_state,verify_event
from .sales_models import CommercialSale,SaleEvent
class Store:
    def __init__(self,crm_store):
        self.base=crm_store;self.scope=crm_store.scope;self.provider=crm_store.provider
        tables=set(connection.introspection.table_names())
        if any(m._meta.db_table not in tables for m in (CommercialSale,SaleEvent)):raise CRMError('SALE_SCHEMA_INSTALL_REQUIRED',503)
    def transaction(self):return self.base.transaction()
    def lock(self):return self.base.lock()
    def get(self,ref):
        row=CommercialSale.objects.filter(pk=ref,scope=self.scope,provider_ref=self.provider).first()
        if not row:return None
        verify_state(row.document,row.id,row.revision,{'code':row.code,'status':row.status},'SALE_INTEGRITY_REVIEW_REQUIRED')
        if digest(row.document)!=row.document_digest:raise CRMError('SALE_INTEGRITY_REVIEW_REQUIRED',503)
        return row.document
    def list(self,q,stage,offset,limit):
        rows=CommercialSale.objects.filter(scope=self.scope,provider_ref=self.provider)
        if q:rows=rows.filter(document__title__icontains=q)
        result=list(rows.order_by('pk')[offset:offset+limit+1]);return [self.get(row.pk) for row in result[:limit]],len(result)>limit
    def save(self,item,expected):
        row=CommercialSale.objects.filter(pk=item['id'],scope=self.scope,provider_ref=self.provider).first()
        if row and row.revision!=expected:raise CRMError('REVISION_CONFLICT',409)
        if row is None:
            if expected:raise CRMError('REVISION_CONFLICT',409)
            row=CommercialSale(id=item['id'],scope=self.scope,provider_ref=self.provider)
        row.code=item['code'];row.revision=item['revision'];row.status=item['status'];row.document=item;row.document_digest=digest(item);row.save()
    def find_code(self,code):
        from django.db.models import Q
        rows=list(CommercialSale.objects.filter(scope=self.scope,provider_ref=self.provider).filter(Q(code=code)|Q(document__code=code)))
        for row in rows:self.get(row.pk)
        return bool(rows)

    @staticmethod
    def _checked_event(row):
        if row is None:return None
        return verify_event(row.document,row.id,row.scope,'item_id',row.item_id,'SALE_EVENT_BINDING_REVIEW_REQUIRED')
    def event(self,rid):
        row=SaleEvent.objects.filter(id=rid).first();return self._checked_event(row)
    def append(self,event):
        verify_event(event,event.get('id'),self.scope,'item_id',event.get('item_id'),'SALE_EVENT_BINDING_REVIEW_REQUIRED')
        SaleEvent.objects.create(id=event['id'],scope=self.scope,item_id=event['item_id'],document=event)
    def events(self,ref):
        for row in SaleEvent.objects.filter(scope=self.scope,item_id=ref).order_by('sequence').only('id','scope','item_id','document').iterator(chunk_size=50):yield self._checked_event(row)
    def last_event(self,ref):
        row=SaleEvent.objects.filter(scope=self.scope,item_id=ref).order_by('-sequence').first();return self._checked_event(row)

    def outbox(self,item,phase):
        import uuid
        from .contract import SYSTEM
        from apps.core_erp.outbox_models import OutboxEvent
        ref=uuid.uuid5(uuid.NAMESPACE_URL,'commercial-sale:'+SYSTEM+':'+item['id']+':'+phase)
        OutboxEvent.objects.create(id=ref,event_type='commercial.sale.'+phase.lower()+'.v1',domain='commercial',aggregate_root=item['id'],payload={'company_id':self.scope,'provider_id':self.provider,'sale_id':item['id'],'quotation_id':item['quotation_id'],'source_digest':item['source']['content_digest'],'journal':item['journal'],'reversal':item['reversal'],'operation_refs':item['operation_refs'],'documents':item['review']['terms']['documents'],'fiscal_document_issued':False,'money_transferred':False},status='PENDING')

    def ensure_no_live_payment(self,sale):
        from .payment_models import CommercialPayment
        if CommercialPayment._meta.db_table not in connection.introspection.table_names():return
        for row in CommercialPayment.objects.filter(scope=self.scope,provider_ref=self.provider,document__sale_id=sale['id']):
            if digest(row.document)!=row.document_digest or row.status!=row.document['status']:raise CRMError('PAYMENT_INTEGRITY_REVIEW_REQUIRED',503)
            if row.document['status'] in ('DISPATCHING','UNKNOWN','CHECKOUT_READY'):raise CRMError('BOLD_PAYMENT_RECONCILIATION_REQUIRED',409)
