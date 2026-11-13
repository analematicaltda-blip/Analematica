from contextlib import contextmanager
from types import SimpleNamespace
from starlette.datastructures import QueryParams
from app.db.session import SessionLocal
from app.models.user import Usuario
from .inbox_models import InboxRecord
from .crm_api import service
from .crm import CRMError

def candidates():
    with SessionLocal() as db:
        rows=[(r.id,r.document) for r in db.query(InboxRecord).filter_by(status='QUEUED').order_by(InboxRecord.id).limit(501)]
    if len(rows)>500:raise CRMError('INBOX_GLOBAL_QUEUE_REVIEW_REQUIRED',503)
    return rows
@contextmanager
def context(document):
    with SessionLocal() as db:
        actor=document.get('creator_ref') if isinstance(document,dict) else None
        if not str(actor).isdigit():raise CRMError('GENERATION_ACTOR_REQUIRED',403)
        user=db.get(Usuario,int(actor))
        if not user or not user.activo:raise CRMError('GENERATION_ACTOR_REQUIRED',403)
        yield service(SimpleNamespace(method='POST',query_params=QueryParams()),db,user)
