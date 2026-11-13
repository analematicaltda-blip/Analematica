from django.db import connection
from .crm import CRMError,digest
from .state_integrity import verify_state,verify_event
from .library_models import LibraryItem,LibraryEvent,LibraryBlob
class Store:
    def __init__(self,crm_store):
        self.base=crm_store;self.scope=crm_store.scope;self.provider=crm_store.provider
        tables=set(connection.introspection.table_names())
        if any(m._meta.db_table not in tables for m in (LibraryItem,LibraryEvent,LibraryBlob)):raise CRMError('LIBRARY_SCHEMA_INSTALL_REQUIRED',503)
    def transaction(self):return self.base.transaction()
    def lock(self):return self.base.lock()
    def get(self,ref):
        row=LibraryItem.objects.filter(pk=ref,scope=self.scope,provider_ref=self.provider).first()
        if not row:return None
        verify_state(row.document,row.id,row.revision,{'code':row.code,'status':row.status},'LIBRARY_INTEGRITY_REVIEW_REQUIRED')
        if digest(row.document)!=row.document_digest or row.code!=row.document['code'] or row.revision!=row.document['revision'] or row.status!=row.document['status']:raise CRMError('LIBRARY_INTEGRITY_REVIEW_REQUIRED',503)
        return row.document
    def list(self,q,stage,offset,limit):
        rows=LibraryItem.objects.filter(scope=self.scope,provider_ref=self.provider)
        if q:rows=rows.filter(document__title__icontains=q)
        result=list(rows.order_by('pk')[offset:offset+limit+1]);return [self.get(row.pk) for row in result[:limit]],len(result)>limit
    def save(self,item,expected):
        row=LibraryItem.objects.filter(pk=item['id'],scope=self.scope,provider_ref=self.provider).first()
        if row and row.revision!=expected:raise CRMError('REVISION_CONFLICT',409)
        if row is None:
            if expected:raise CRMError('REVISION_CONFLICT',409)
            row=LibraryItem(id=item['id'],scope=self.scope,provider_ref=self.provider)
        row.code=item['code'];row.revision=item['revision'];row.status=item['status'];row.document=item;row.document_digest=digest(item);row.save()
    def find_code(self,code):
        from django.db.models import Q
        rows=list(LibraryItem.objects.filter(scope=self.scope,provider_ref=self.provider).filter(Q(code=code)|Q(document__code=code)))
        for row in rows:self.get(row.pk)
        return bool(rows)
    @staticmethod
    def _checked_event(row):
        if row is None:return None
        return verify_event(row.document,row.id,row.scope,'item_id',row.item_id,'LIBRARY_EVENT_BINDING_REVIEW_REQUIRED')
    def event(self,rid):
        row=LibraryEvent.objects.filter(id=rid).first();return self._checked_event(row)
    def append(self,event):
        verify_event(event,event.get('id'),self.scope,'item_id',event.get('item_id'),'LIBRARY_EVENT_BINDING_REVIEW_REQUIRED')
        LibraryEvent.objects.create(id=event['id'],scope=self.scope,item_id=event['item_id'],document=event)
    def events(self,ref):
        for row in LibraryEvent.objects.filter(scope=self.scope,item_id=ref).order_by('sequence').only('id','scope','item_id','document').iterator(chunk_size=50):yield self._checked_event(row)
    def last_event(self,ref):
        row=LibraryEvent.objects.filter(scope=self.scope,item_id=ref).order_by('-sequence').first();return self._checked_event(row)



    def blob(self,ref):
        row=LibraryBlob.objects.filter(pk=ref,scope=self.scope,provider_ref=self.provider).first()
        return {'original':bytes(row.original),'delivery':bytes(row.delivery),'original_sha':row.original_sha,'delivery_sha':row.delivery_sha,'mime':row.mime} if row else None
    def save_blob(self,ref,original,delivery,original_sha,delivery_sha,mime):LibraryBlob.objects.create(id=ref,scope=self.scope,provider_ref=self.provider,original=original,delivery=delivery,original_sha=original_sha,delivery_sha=delivery_sha,mime=mime)
    def usage(self):
        from django.db.models import Sum
        from django.db.models.functions import Length
        rows=LibraryBlob.objects.filter(scope=self.scope,provider_ref=self.provider)
        return rows.count(),int(rows.aggregate(size=Sum(Length('original')+Length('delivery')))['size'] or 0)
    @classmethod
    def public_scope(cls,db,ref):
        row=LibraryItem.objects.filter(pk=ref).first()
        return {'scope':row.scope,'provider':row.provider_ref,'document':row.document} if row else None
