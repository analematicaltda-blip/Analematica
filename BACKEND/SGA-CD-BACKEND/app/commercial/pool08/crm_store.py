"""ORM adapter: all existing WorkspaceLead rows remain visible with the same ID."""
from contextlib import contextmanager
from datetime import datetime,timezone
from sqlalchemy import or_,inspect
from sqlalchemy.exc import IntegrityError,OperationalError
from app.models.workspace import WorkspaceLead
from app.models.tenancy import Inquilino
from .crm_models import CRMContact,CRMEvent
from .crm import CRMError,digest

from .contract import SYSTEM

class Store:
    system=SYSTEM
    def __init__(self,db,access):
        self.db,self.scope,self.actor,self.tenant=db,access.scope,access.user.id,access.tenant.id
        self.company_name=access.tenant.nombre_empresa
        inspector=inspect(db.get_bind())
        for model in (CRMContact,CRMEvent):
            if not inspector.has_table(model.__tablename__) or not {c.name for c in model.__table__.columns}<={c['name'] for c in inspector.get_columns(model.__tablename__)}:
                raise CRMError('CRM_SCHEMA_INSTALL_REQUIRED',503)
    @contextmanager
    def transaction(self):
        try:
            yield
            self.db.commit()
        except (IntegrityError,OperationalError):
            self.db.rollback();raise CRMError('CRM_WRITE_CONFLICT',409) from None
        except Exception:
            self.db.rollback();raise
    def lock(self):
        # Serializes dedup checks and writes per tenant on PostgreSQL and SQLite.
        count=self.db.query(Inquilino).filter_by(id=self.tenant).update({Inquilino.activo:Inquilino.activo},synchronize_session=False)
        if count!=1:raise CRMError('COMPANY_NOT_AVAILABLE',403)
    def base(self,cid):
        return self.db.query(WorkspaceLead).populate_existing().filter_by(id=cid,scope=self.scope).first()
    def snapshot(self,row):return dict(name=row.name,email=row.email,notes=row.notes,stage=row.stage)
    def get(self,cid):
        row=self.base(cid)
        if row is None:return None
        base=self.snapshot(row)
        meta=self.db.query(CRMContact).populate_existing().filter_by(id=cid,scope=self.scope).first()
        if meta:
            if meta.base_fingerprint!=digest(base):raise CRMError('LEGACY_CONTACT_CHANGED_REVIEW_REQUIRED',409)
            return meta.document
        return {**base,'id':cid,'email':row.email.strip().casefold(),'phone':'','origin':'LEGACY_WORKSPACE',
                'responsible_ref':str(row.created_by),'revision':0,'status':'PROSPECT','consents':{},'tasks':[],
                'duplicate_review':None,'customer_ref':None}
    def list(self,query,offset,limit):
        q=self.db.query(WorkspaceLead).filter_by(scope=self.scope).order_by(WorkspaceLead.id)
        if query:
            # The query is a parameter, and wildcard characters have literal meaning.
            escaped=query.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
            q=q.filter(or_(WorkspaceLead.name.ilike('%'+escaped+'%',escape='\\'),WorkspaceLead.email.ilike('%'+escaped+'%',escape='\\')))
        rows=q.offset(offset).limit(limit+1).all()
        return [self.get(r.id) for r in rows[:limit]],len(rows)>limit
    def duplicates(self,email,phone,excluding):
        result=[]
        for row in self.db.query(WorkspaceLead).filter_by(scope=self.scope).yield_per(100):
            if row.id==excluding:continue
            value=self.get(row.id)
            if (email and email==value['email']) or (phone and phone==value['phone']):result.append(row.id)
        return sorted(result)
    def save(self,item,revision):
        row=self.base(item['id']);meta=self.db.query(CRMContact).filter_by(id=item['id'],scope=self.scope).first()
        if meta and meta.revision!=revision:raise CRMError('REVISION_CONFLICT',409)
        if row is None:
            if revision:raise CRMError('CONTACT_NOT_FOUND',404)
            row=WorkspaceLead(id=item['id'],scope=self.scope,created_by=self.actor);self.db.add(row)
        row.name,row.email,row.notes,row.stage=(item[key] for key in ('name','email','notes','stage'))
        if item['status']=='CUSTOMER':item['customer_ref']='workspace:'+item['id']
        if meta is None:meta=CRMContact(id=item['id'],scope=self.scope);self.db.add(meta)
        meta.revision=item['revision'];meta.document=item;meta.base_fingerprint=digest(self.snapshot(row));self.db.flush()
    def event(self,rid):
        row=self.db.query(CRMEvent).filter_by(id=rid).first();return row.document if row else None
    def append(self,rid,actor,operation,contact,fingerprint,receipt,data):
        document=dict(scope=self.scope,actor=actor,operation=operation,contact_id=contact,fingerprint=fingerprint,receipt=receipt,data=data,created_at=datetime.now(timezone.utc).isoformat())
        self.db.add(CRMEvent(id=rid,scope=self.scope,contact=contact,document=document));self.db.flush()
    def history(self,contact,offset,limit):
        return [row.document for row in self.db.query(CRMEvent).filter_by(scope=self.scope,contact=contact).order_by(CRMEvent.sequence).offset(offset).limit(limit).all()]
