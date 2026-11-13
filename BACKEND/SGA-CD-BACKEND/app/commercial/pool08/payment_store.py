"""SQLAlchemy opportunity adapter on the same transactional database as the CRM."""
from sqlalchemy import inspect
from .crm import CRMError,digest
from .state_integrity import verify_state,verify_event
from .payment_models import CommercialPayment,PaymentEvent
class Store:
    def __init__(self,crm_store):
        self.base=crm_store;self.db=crm_store.db;self.scope=crm_store.scope
        inspector=inspect(self.db.get_bind())
        for model in (CommercialPayment,PaymentEvent):
            if not inspector.has_table(model.__tablename__):raise CRMError('PAYMENT_SCHEMA_INSTALL_REQUIRED',503)
    def transaction(self):return self.base.transaction()
    def lock(self):return self.base.lock()
    def get(self,ref):
        row=self.db.query(CommercialPayment).populate_existing().filter_by(id=ref,scope=self.scope).first()
        if row is None:return None
        verify_state(row.document,row.id,row.revision,{'code':row.code,'status':row.status},'PAYMENT_INTEGRITY_REVIEW_REQUIRED')
        if digest(row.document)!=row.document_digest or row.code!=row.document['code'] or row.revision!=row.document['revision'] or row.status!=row.document['status']:raise CRMError('PAYMENT_INTEGRITY_REVIEW_REQUIRED',503)
        return row.document
    def list(self,q,stage,offset,limit):
        rows=self.db.query(CommercialPayment).filter_by(scope=self.scope)
        if stage:rows=rows.filter_by(status=stage)
        if q:
            escaped=q.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
            rows=rows.filter(CommercialPayment.document['title'].as_string().ilike('%'+escaped+'%',escape='\\'))
        result=rows.order_by(CommercialPayment.id).offset(offset).limit(limit+1).all()
        return [self.get(row.id) for row in result[:limit]],len(result)>limit
    def save(self,item,expected):
        row=self.db.query(CommercialPayment).filter_by(id=item['id'],scope=self.scope).first()
        if row is None:
            if expected!=0:raise CRMError('REVISION_CONFLICT',409)
            row=CommercialPayment(id=item['id'],scope=self.scope);self.db.add(row)
        elif row.revision!=expected:raise CRMError('REVISION_CONFLICT',409)
        row.code=item['code'];row.revision=item['revision'];row.status=item['status'];row.document=item;row.document_digest=digest(item);self.db.flush()
    @staticmethod
    def _checked_event(row):
        if row is None:return None
        return verify_event(row.document,row.id,row.scope,'item_id',row.item_id,'PAYMENT_EVENT_BINDING_REVIEW_REQUIRED')
    def event(self,rid):
        row=self.db.query(PaymentEvent).filter_by(id=rid).first();return self._checked_event(row)
    def append(self,event):
        verify_event(event,event.get('id'),self.scope,'item_id',event.get('item_id'),'PAYMENT_EVENT_BINDING_REVIEW_REQUIRED')
        self.db.add(PaymentEvent(id=event['id'],scope=self.scope,item_id=event['item_id'],document=event));self.db.flush()
    def events(self,ref):
        for row in self.db.query(PaymentEvent).filter_by(scope=self.scope,item_id=ref).order_by(PaymentEvent.sequence).yield_per(50):yield self._checked_event(row)

    def last_event(self,ref):
        row=self.db.query(PaymentEvent).filter_by(scope=self.scope,item_id=ref).order_by(PaymentEvent.sequence.desc()).first()
        return self._checked_event(row)

    def legacy_history(self,ref):return []

    def find_code(self,code):
        from sqlalchemy import or_
        rows=self.db.query(CommercialPayment).filter(CommercialPayment.scope==self.scope,or_(CommercialPayment.code==code,CommercialPayment.document['code'].as_string()==code)).all()
        for row in rows:self.get(row.id)
        return bool(rows)


