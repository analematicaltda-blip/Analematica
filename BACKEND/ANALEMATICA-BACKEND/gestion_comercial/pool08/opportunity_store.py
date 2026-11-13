"""Django opportunity adapter, with explicit adoption of ERP's existing Opportunity."""
from django.db import connection
from .crm import CRMError,digest
from .state_integrity import verify_state,verify_event
from .contract import SYSTEM
from .opportunity_models import CommercialOpportunity,OpportunityEvent
class Store:
    def __init__(self,crm_store):
        self.base=crm_store;self.scope=crm_store.scope;self.provider=crm_store.provider
        self.legacy=None
        if SYSTEM=='erp-tur':
            from ..sales.models import Opportunity,StageHistory
            self.legacy=Opportunity;self.history_model=StageHistory
        tables=set(connection.introspection.table_names())
        for model in (CommercialOpportunity,OpportunityEvent,*((self.legacy,self.history_model) if self.legacy else ())):
            if model._meta.db_table not in tables:raise CRMError('OPPORTUNITY_SCHEMA_INSTALL_REQUIRED',503)
    def transaction(self):return self.base.transaction()
    def lock(self):return self.base.lock()
    def legacy_rows(self):return self.legacy.objects.filter(provider_id=self.provider,is_active=True)
    def legacy_history(self,ref):
        if not self.legacy:return []
        if not self.legacy_rows().filter(pk=ref).exists():raise CRMError('OPPORTUNITY_NOT_FOUND',404)
        return [{'id':str(row.pk),'from_stage':row.from_stage,'to_stage':row.to_stage,'actor_ref':str(row.user_id) if row.user_id else None,'created_at':row.timestamp.isoformat(),'source':'EXISTING_STAGE_HISTORY','authenticity_verified':False} for row in self.history_model.objects.filter(opportunity_id=ref).order_by('timestamp','pk').iterator(chunk_size=100)]
    def snapshot(self,row):
        history=self.legacy_history(str(row.pk))
        return {'id':str(row.pk),'title':row.name,'stage':row.stage,'value':str(row.value),'responsible_ref':str(row.owner_id) if row.owner_id else None,'provider_ref':str(row.provider_id),'is_active':row.is_active,'legacy_history_digest':digest(history),'legacy_history_count':len(history)}
    def legacy_item(self,row):
        snapshot=self.snapshot(row)
        return {'id':str(row.pk),'title':row.name,'stage':row.stage.strip().upper(),'value':str(row.value),'responsible_ref':snapshot['responsible_ref'],
                'currency':None,'notes':'','next_action':None,'interest_evidence':None,'contact_id':None,'revision':0,'requires_adoption':True,'legacy_snapshot':snapshot}
    def get(self,ref):
        meta=CommercialOpportunity.objects.filter(pk=ref,scope=self.scope,provider_ref=self.provider).first()
        if meta:
            verify_state(meta.document,meta.pk,meta.revision,{'stage':meta.stage},'OPPORTUNITY_INTEGRITY_REVIEW_REQUIRED')
            if digest(meta.document)!=meta.document_digest:raise CRMError('OPPORTUNITY_INTEGRITY_REVIEW_REQUIRED',503)
            if self.legacy:
                row=self.legacy_rows().filter(pk=meta.legacy_ref).first()
                if row is None or digest(self.snapshot(row))!=meta.base_fingerprint:raise CRMError('LEGACY_OPPORTUNITY_CHANGED_REVIEW_REQUIRED',409)
            return meta.document
        if self.legacy:
            row=self.legacy_rows().filter(pk=ref).first()
            if row:return self.legacy_item(row)
        return None
    def list(self,q,stage,offset,limit):
        from itertools import islice
        from heapq import merge
        metas=CommercialOpportunity.objects.filter(scope=self.scope,provider_ref=self.provider)
        if q:metas=metas.filter(document__title__icontains=q)
        if stage:metas=metas.filter(stage=stage)
        stream=(self.get(row.pk) for row in metas.order_by('pk').iterator(chunk_size=100))
        if self.legacy:
            known=CommercialOpportunity.objects.filter(scope=self.scope).exclude(legacy_ref=None).values_list('legacy_ref',flat=True)
            legacy=self.legacy_rows().exclude(pk__in=known)
            if q:legacy=legacy.filter(name__icontains=q)
            if stage:legacy=legacy.filter(stage__iexact=stage)
            legacy_stream=(self.legacy_item(row) for row in legacy.order_by('pk').iterator(chunk_size=100))
            stream=merge(stream,legacy_stream,key=lambda item:item['id'])
        result=list(islice(stream,offset,offset+limit+1));return result[:limit],len(result)>limit
    def save(self,item,expected):
        meta=CommercialOpportunity.objects.filter(pk=item['id'],scope=self.scope,provider_ref=self.provider).first()
        if meta and meta.revision!=expected:raise CRMError('REVISION_CONFLICT',409)
        if meta is None:meta=CommercialOpportunity(id=item['id'],scope=self.scope,provider_ref=self.provider)
        fingerprint=digest({})
        if self.legacy:
            from decimal import Decimal
            row=self.legacy_rows().filter(pk=item['id']).first();previous=row.stage if row else None
            if row is None:
                if expected:raise CRMError('OPPORTUNITY_NOT_FOUND',404)
                row=self.legacy(id=item['id'],provider_id=self.provider)
            row.name=item['title'];row.stage=item['stage'].title();row.value=Decimal(item['value']);row.owner_id=int(item['responsible_ref']);row.save()
            from decimal import InvalidOperation
            try:row.refresh_from_db()
            except InvalidOperation:raise CRMError('VALUE_PRECISION_NOT_SUPPORTED') from None
            if row.value!=Decimal(item['value']):raise CRMError('VALUE_PRECISION_NOT_SUPPORTED')
            if previous!=row.stage:self.history_model.objects.create(opportunity=row,from_stage=previous or '',to_stage=row.stage,user_id=int(self.base.actor))
            meta.legacy_ref=str(row.pk);fingerprint=digest(self.snapshot(row))
        meta.revision=item['revision'];meta.stage=item['stage'];meta.document=item;meta.document_digest=digest(item);meta.base_fingerprint=fingerprint;meta.save()
    @staticmethod
    def _checked_event(row):
        if row is None:return None
        return verify_event(row.document,row.id,row.scope,'opportunity_id',row.opportunity,'OPPORTUNITY_EVENT_BINDING_REVIEW_REQUIRED')
    def event(self,rid):
        row=OpportunityEvent.objects.filter(id=rid).first();return self._checked_event(row)
    def append(self,event):
        verify_event(event,event.get('id'),self.scope,'opportunity_id',event.get('opportunity_id'),'OPPORTUNITY_EVENT_BINDING_REVIEW_REQUIRED')
        OpportunityEvent.objects.create(id=event['id'],scope=self.scope,opportunity=event['opportunity_id'],document=event)
    def events(self,ref):
        for row in OpportunityEvent.objects.filter(scope=self.scope,opportunity=ref).order_by('sequence').only('id','scope','opportunity','document').iterator(chunk_size=50):yield self._checked_event(row)

    def last_event(self,ref):
        row=OpportunityEvent.objects.filter(scope=self.scope,opportunity=ref).order_by('-sequence').first()
        return self._checked_event(row)
