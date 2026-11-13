from django.db import connection
from .crm import CRMError,digest
from .state_integrity import verify_state,verify_event
from .capture_models import LandingCapture,CaptureEvent
class Store:
    def __init__(self,crm_store):
        self.base=crm_store;self.scope=crm_store.scope;self.provider=crm_store.provider
        tables=set(connection.introspection.table_names())
        if any(m._meta.db_table not in tables for m in (LandingCapture,CaptureEvent)):raise CRMError('CAPTURE_SCHEMA_INSTALL_REQUIRED',503)
    def transaction(self):return self.base.transaction()
    def lock(self):return self.base.lock()
    def get(self,ref):
        row=LandingCapture.objects.filter(pk=ref,scope=self.scope,provider_ref=self.provider).first()
        if not row:return None
        verify_state(row.document,row.id,row.revision,{'code':row.code,'status':row.status},'CAPTURE_INTEGRITY_REVIEW_REQUIRED')
        if digest(row.document)!=row.document_digest or row.code!=row.document['code'] or row.revision!=row.document['revision'] or row.status!=row.document['status']:raise CRMError('CAPTURE_INTEGRITY_REVIEW_REQUIRED',503)
        return row.document
    def list(self,q,stage,offset,limit):
        rows=LandingCapture.objects.filter(scope=self.scope,provider_ref=self.provider)
        if q:rows=rows.filter(document__title__icontains=q)
        result=list(rows.order_by('pk')[offset:offset+limit+1]);return [self.get(row.pk) for row in result[:limit]],len(result)>limit
    def save(self,item,expected):
        row=LandingCapture.objects.filter(pk=item['id'],scope=self.scope,provider_ref=self.provider).first()
        if row and row.revision!=expected:raise CRMError('REVISION_CONFLICT',409)
        if row is None:
            if expected:raise CRMError('REVISION_CONFLICT',409)
            row=LandingCapture(id=item['id'],scope=self.scope,provider_ref=self.provider)
        row.code=item['code'];row.revision=item['revision'];row.status=item['status'];row.document=item;row.document_digest=digest(item);row.save()
    def find_code(self,code):
        from django.db.models import Q
        rows=list(LandingCapture.objects.filter(scope=self.scope,provider_ref=self.provider).filter(Q(code=code)|Q(document__code=code)))
        for row in rows:self.get(row.pk)
        return bool(rows)
    @staticmethod
    def _checked_event(row):
        if row is None:return None
        return verify_event(row.document,row.id,row.scope,'item_id',row.item_id,'CAPTURE_EVENT_BINDING_REVIEW_REQUIRED')
    def event(self,rid):
        row=CaptureEvent.objects.filter(id=rid).first();return self._checked_event(row)
    def append(self,event):
        verify_event(event,event.get('id'),self.scope,'item_id',event.get('item_id'),'CAPTURE_EVENT_BINDING_REVIEW_REQUIRED')
        CaptureEvent.objects.create(id=event['id'],scope=self.scope,item_id=event['item_id'],document=event)
    def events(self,ref):
        for row in CaptureEvent.objects.filter(scope=self.scope,item_id=ref).order_by('sequence').only('id','scope','item_id','document').iterator(chunk_size=50):yield self._checked_event(row)
    def last_event(self,ref):
        row=CaptureEvent.objects.filter(scope=self.scope,item_id=ref).order_by('-sequence').first();return self._checked_event(row)



    def recent(self,ip_digest,since):
        return LandingCapture.objects.filter(scope=self.scope,provider_ref=self.provider,document__ip_digest=ip_digest,document__created_at__gte=since).count()

    def by_page(self,ref,offset,limit):
        rows=list(LandingCapture.objects.filter(scope=self.scope,provider_ref=self.provider,document__page_id=ref).order_by('pk')[offset:offset+limit+1])
        return [self.get(row.pk) for row in rows[:limit]],len(rows)>limit
    def metrics(self,ref):
        q=LandingCapture.objects.filter(scope=self.scope,provider_ref=self.provider,document__page_id=ref)
        return {'accepted_submissions':q.count(),'created_prospects':q.filter(document__created_contact=True).count(),'review_required':q.filter(document__requires_review=True).count(),'withdrawn':q.filter(status='WITHDRAWN').count()}
