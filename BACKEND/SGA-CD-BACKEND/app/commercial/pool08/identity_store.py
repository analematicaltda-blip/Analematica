"""SQLAlchemy storage owned by SGA-CD; installation is explicit and additive."""
from contextlib import contextmanager
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError, OperationalError
from . import identity_models as models
from .access_protocol import AccessFault
MODELS={'grant':models.CommercialGrant,'consent':models.CommercialConsent,'alias':models.CommercialIdentityAlias,'event':models.CommercialPolicyEvent}
class Store:
    def __init__(self,db):self.db=db
    def exists(self,kind):return inspect(self.db.get_bind()).has_table(MODELS[kind].__tablename__)
    def ready(self):return all(self.exists(kind) for kind in MODELS)
    def row(self,item):return {column.key:getattr(item,column.key) for column in item.__table__.columns} if item else None
    def get(self,kind,tenant,**filters):
        if not self.exists(kind):return None
        return self.row(self.db.query(MODELS[kind]).populate_existing().filter_by(tenant_ref=tenant,**filters).first())
    def get_by_id(self,kind,key):
        return self.row(self.db.query(MODELS[kind]).populate_existing().filter_by(id=key).first())
    def list(self,kind,tenant,limit):
        model=MODELS[kind]
        return [self.row(row) for row in self.db.query(model).filter_by(tenant_ref=tenant).order_by(model.created_at.desc(),model.id).limit(limit)]
    def save(self,kind,row,expected):
        model=MODELS[kind]
        if expected==0:self.db.add(model(**row));self.db.flush()
        else:
            count=self.db.query(model).filter_by(id=row['id'],tenant_ref=row['tenant_ref'],revision=expected).update(row,synchronize_session=False)
            if count!=1:raise AccessFault('REVISION_CONFLICT',409)
            self.db.flush()
    @contextmanager
    def transaction(self):
        try:
            yield
            self.db.commit()
        except (IntegrityError,OperationalError):
            self.db.rollback();raise AccessFault('ACCESS_WRITE_CONFLICT',409) from None
        except BaseException:
            self.db.rollback();raise
