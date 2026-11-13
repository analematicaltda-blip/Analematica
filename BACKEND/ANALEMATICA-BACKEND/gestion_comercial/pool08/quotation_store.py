from django.db import connection
from .crm import CRMError,digest
from .state_integrity import verify_state,verify_event
from .quotation_models import CommercialQuotation,QuotationEvent,QuotationAsset
class Store:
    def __init__(self,crm_store):
        self.base=crm_store;self.scope=crm_store.scope;self.provider=crm_store.provider
        tables=set(connection.introspection.table_names())
        if any(m._meta.db_table not in tables for m in (CommercialQuotation,QuotationEvent,QuotationAsset)):raise CRMError('QUOTE_SCHEMA_INSTALL_REQUIRED',503)
        with connection.cursor() as cursor:
            columns={c.name for c in connection.introspection.get_table_description(cursor,QuotationAsset._meta.db_table)}
        if 'provider_ref' not in columns:raise CRMError('QUOTE_MEDIA_PROVIDER_MIGRATION_REQUIRED',503)
    def transaction(self):return self.base.transaction()
    def lock(self):return self.base.lock()
    def get(self,ref):
        row=CommercialQuotation.objects.filter(pk=ref,scope=self.scope,provider_ref=self.provider).first()
        if not row:return None
        verify_state(row.document,row.id,row.revision,{'code':row.code,'status':row.status},'QUOTE_INTEGRITY_REVIEW_REQUIRED')
        if digest(row.document)!=row.document_digest:raise CRMError('QUOTE_INTEGRITY_REVIEW_REQUIRED',503)
        return row.document
    def list(self,q,stage,offset,limit):
        rows=CommercialQuotation.objects.filter(scope=self.scope,provider_ref=self.provider).exclude(status='CAPACITY_POLICY')
        if q:rows=rows.filter(document__title__icontains=q)
        result=list(rows.order_by('pk')[offset:offset+limit+1]);return [self.get(row.pk) for row in result[:limit]],len(result)>limit
    def save(self,item,expected):
        row=CommercialQuotation.objects.filter(pk=item['id'],scope=self.scope,provider_ref=self.provider).first()
        if row and row.revision!=expected:raise CRMError('REVISION_CONFLICT',409)
        if row is None:
            if expected:raise CRMError('REVISION_CONFLICT',409)
            row=CommercialQuotation(id=item['id'],scope=self.scope,provider_ref=self.provider)
        row.code=item['code'];row.revision=item['revision'];row.status=item['status'];row.document=item;row.document_digest=digest(item);row.save()
    def find_code(self,code):
        from django.db.models import Q
        rows=list(CommercialQuotation.objects.filter(scope=self.scope,provider_ref=self.provider).filter(Q(code=code)|Q(document__code=code)))
        for row in rows:self.get(row.pk)
        return bool(rows)

    @staticmethod
    def _checked_event(row):
        if row is None:return None
        return verify_event(row.document,row.id,row.scope,'item_id',row.item_id,'QUOTE_EVENT_BINDING_REVIEW_REQUIRED')
    def event(self,rid):
        row=QuotationEvent.objects.filter(id=rid).first();return self._checked_event(row)
    def append(self,event):
        verify_event(event,event.get('id'),self.scope,'item_id',event.get('item_id'),'QUOTE_EVENT_BINDING_REVIEW_REQUIRED')
        QuotationEvent.objects.create(id=event['id'],scope=self.scope,item_id=event['item_id'],document=event)
    def events(self,ref):
        for row in QuotationEvent.objects.filter(scope=self.scope,item_id=ref).order_by('sequence').only('id','scope','item_id','document').iterator(chunk_size=50):yield self._checked_event(row)
    def last_event(self,ref):
        row=QuotationEvent.objects.filter(scope=self.scope,item_id=ref).order_by('-sequence').first();return self._checked_event(row)

    def policy(self,ref,revision):
        from django.db.models import Q
        code='CAP:'+ref+':'+str(revision)
        row=CommercialQuotation.objects.filter(scope=self.scope,provider_ref=self.provider).filter(Q(code=code)|Q(document__code=code)).first();return self.get(row.pk) if row else None
    def asset(self,ref):
        row=QuotationAsset.objects.filter(pk=ref,scope=self.scope,provider_ref=self.provider).first()
        return {**{k:getattr(row,k) for k in ('id','scope','creator_ref','mime','digest','original_digest')},'data':bytes(row.data)} if row else None
    def save_asset(self,ref,actor,data,mime,digest,original):QuotationAsset.objects.create(id=ref,scope=self.scope,provider_ref=self.provider,creator_ref=actor,data=data,mime=mime,digest=digest,original_digest=original)
    def asset_usage(self):
        from django.db.models import Count,Sum
        from django.db.models.functions import Length
        result=QuotationAsset.objects.filter(scope=self.scope,provider_ref=self.provider).aggregate(count=Count('id'),size=Sum(Length('data')));return result['count'] or 0,result['size'] or 0
