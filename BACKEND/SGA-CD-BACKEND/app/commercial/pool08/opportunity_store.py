"""SQLAlchemy opportunity adapter on the same transactional database as the CRM."""
from sqlalchemy import inspect
from .crm import CRMError,digest
from .state_integrity import verify_state,verify_event
from .opportunity_models import CommercialOpportunity,OpportunityEvent
class Store:
    def __init__(self,crm_store):
        self.base=crm_store;self.db=crm_store.db;self.scope=crm_store.scope
        inspector=inspect(self.db.get_bind())
        for model in (CommercialOpportunity,OpportunityEvent):
            if not inspector.has_table(model.__tablename__):raise CRMError('OPPORTUNITY_SCHEMA_INSTALL_REQUIRED',503)
    def transaction(self):return self.base.transaction()
    def lock(self):return self.base.lock()
    def get(self,ref):
        row=self.db.query(CommercialOpportunity).populate_existing().filter_by(id=ref,scope=self.scope).first()
        if row is None:return None
        verify_state(row.document,row.id,row.revision,{'stage':row.stage},'OPPORTUNITY_INTEGRITY_REVIEW_REQUIRED')
        if digest(row.document)!=row.document_digest:raise CRMError('OPPORTUNITY_INTEGRITY_REVIEW_REQUIRED',503)
        return row.document
    def list(self,q,stage,offset,limit):
        rows=self.db.query(CommercialOpportunity).filter_by(scope=self.scope)
        if stage:rows=rows.filter_by(stage=stage)
        if q:
            escaped=q.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
            rows=rows.filter(CommercialOpportunity.document['title'].as_string().ilike('%'+escaped+'%',escape='\\'))
        result=rows.order_by(CommercialOpportunity.id).offset(offset).limit(limit+1).all()
        return [self.get(row.id) for row in result[:limit]],len(result)>limit
    def save(self,item,expected):
        row=self.db.query(CommercialOpportunity).filter_by(id=item['id'],scope=self.scope).first()
        if row is None:
            if expected!=0:raise CRMError('REVISION_CONFLICT',409)
            row=CommercialOpportunity(id=item['id'],scope=self.scope);self.db.add(row)
        elif row.revision!=expected:raise CRMError('REVISION_CONFLICT',409)
        row.revision=item['revision'];row.stage=item['stage'];row.document=item;row.document_digest=digest(item);self.db.flush()
    @staticmethod
    def _checked_event(row):
        if row is None:return None
        return verify_event(row.document,row.id,row.scope,'opportunity_id',row.opportunity,'OPPORTUNITY_EVENT_BINDING_REVIEW_REQUIRED')
    def event(self,rid):
        row=self.db.query(OpportunityEvent).filter_by(id=rid).first();return self._checked_event(row)
    def append(self,event):
        verify_event(event,event.get('id'),self.scope,'opportunity_id',event.get('opportunity_id'),'OPPORTUNITY_EVENT_BINDING_REVIEW_REQUIRED')
        self.db.add(OpportunityEvent(id=event['id'],scope=self.scope,opportunity=event['opportunity_id'],document=event));self.db.flush()
    def events(self,ref):
        for row in self.db.query(OpportunityEvent).filter_by(scope=self.scope,opportunity=ref).order_by(OpportunityEvent.sequence).yield_per(50):yield self._checked_event(row)

    def last_event(self,ref):
        row=self.db.query(OpportunityEvent).filter_by(scope=self.scope,opportunity=ref).order_by(OpportunityEvent.sequence.desc()).first()
        return self._checked_event(row)

    def legacy_history(self,ref):return []
