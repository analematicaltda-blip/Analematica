"""SQLAlchemy opportunity adapter on the same transactional database as the CRM."""
from sqlalchemy import inspect
from .crm import CRMError,digest
from .state_integrity import verify_state,verify_event
from .sales_models import CommercialSale,SaleEvent
class Store:
    def __init__(self,crm_store):
        self.base=crm_store;self.db=crm_store.db;self.scope=crm_store.scope
        inspector=inspect(self.db.get_bind())
        for model in (CommercialSale,SaleEvent):
            if not inspector.has_table(model.__tablename__):raise CRMError('SALE_SCHEMA_INSTALL_REQUIRED',503)
    def transaction(self):return self.base.transaction()
    def lock(self):return self.base.lock()
    def get(self,ref):
        row=self.db.query(CommercialSale).populate_existing().filter_by(id=ref,scope=self.scope).first()
        if row is None:return None
        verify_state(row.document,row.id,row.revision,{'code':row.code,'status':row.status},'SALE_INTEGRITY_REVIEW_REQUIRED')
        if digest(row.document)!=row.document_digest:raise CRMError('SALE_INTEGRITY_REVIEW_REQUIRED',503)
        return row.document
    def list(self,q,stage,offset,limit):
        rows=self.db.query(CommercialSale).filter_by(scope=self.scope)
        if stage:rows=rows.filter_by(status=stage)
        if q:
            escaped=q.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
            rows=rows.filter(CommercialSale.document['title'].as_string().ilike('%'+escaped+'%',escape='\\'))
        result=rows.order_by(CommercialSale.id).offset(offset).limit(limit+1).all()
        return [self.get(row.id) for row in result[:limit]],len(result)>limit
    def save(self,item,expected):
        row=self.db.query(CommercialSale).filter_by(id=item['id'],scope=self.scope).first()
        if row is None:
            if expected!=0:raise CRMError('REVISION_CONFLICT',409)
            row=CommercialSale(id=item['id'],scope=self.scope);self.db.add(row)
        elif row.revision!=expected:raise CRMError('REVISION_CONFLICT',409)
        row.code=item['code'];row.revision=item['revision'];row.status=item['status'];row.document=item;row.document_digest=digest(item);self.db.flush()
    @staticmethod
    def _checked_event(row):
        if row is None:return None
        return verify_event(row.document,row.id,row.scope,'item_id',row.item_id,'SALE_EVENT_BINDING_REVIEW_REQUIRED')
    def event(self,rid):
        row=self.db.query(SaleEvent).filter_by(id=rid).first();return self._checked_event(row)
    def append(self,event):
        verify_event(event,event.get('id'),self.scope,'item_id',event.get('item_id'),'SALE_EVENT_BINDING_REVIEW_REQUIRED')
        self.db.add(SaleEvent(id=event['id'],scope=self.scope,item_id=event['item_id'],document=event));self.db.flush()
    def events(self,ref):
        for row in self.db.query(SaleEvent).filter_by(scope=self.scope,item_id=ref).order_by(SaleEvent.sequence).yield_per(50):yield self._checked_event(row)

    def last_event(self,ref):
        row=self.db.query(SaleEvent).filter_by(scope=self.scope,item_id=ref).order_by(SaleEvent.sequence.desc()).first()
        return self._checked_event(row)

    def legacy_history(self,ref):return []

    def find_code(self,code):
        from sqlalchemy import or_
        rows=self.db.query(CommercialSale).filter(CommercialSale.scope==self.scope,or_(CommercialSale.code==code,CommercialSale.document['code'].as_string()==code)).all()
        for row in rows:self.get(row.id)
        return bool(rows)

    def ensure_no_live_payment(self,sale):
        from .payment_models import CommercialPayment
        if not inspect(self.db.get_bind()).has_table(CommercialPayment.__tablename__):return
        for row in self.db.query(CommercialPayment).filter(CommercialPayment.scope==self.scope,CommercialPayment.document['sale_id'].as_string()==sale['id']):
            if digest(row.document)!=row.document_digest or row.status!=row.document['status']:raise CRMError('PAYMENT_INTEGRITY_REVIEW_REQUIRED',503)
            if row.document['status'] in ('DISPATCHING','UNKNOWN','CHECKOUT_READY'):raise CRMError('BOLD_PAYMENT_RECONCILIATION_REQUIRED',409)
