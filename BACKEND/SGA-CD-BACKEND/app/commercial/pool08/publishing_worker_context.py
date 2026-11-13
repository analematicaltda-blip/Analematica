from contextlib import contextmanager
from types import SimpleNamespace
from starlette.datastructures import QueryParams
from app.db.session import SessionLocal
from app.models.user import Usuario
from .publishing_models import PublishingRecord
from .crm_api import service
from .crm import CRMError

def candidates():
    from datetime import datetime,timezone
    from .crm import moment
    states=('SCHEDULED','READY_TO_PUBLISH','WAIT_CONTAINER','VERIFY','REMOTE_REVIEW')
    with SessionLocal() as db:
        rows=[(r.id,r.document) for r in db.query(PublishingRecord).filter(PublishingRecord.status.in_(states)).order_by(PublishingRecord.id).limit(501)]
    if len(rows)>500:raise CRMError('PUBLISH_GLOBAL_QUEUE_REVIEW_REQUIRED',503)
    now=datetime.now(timezone.utc)
    return sorted([(ref,d) for ref,d in rows if moment(d['scheduled_at'])<=now and (not d.get('next_poll_at') or moment(d['next_poll_at'])<=now)],key=lambda row:(row[1]['scheduled_at'],row[0]))
@contextmanager
def context(document):
    with SessionLocal() as db:
        actor=document.get('creator_ref') if isinstance(document,dict) else None
        if not str(actor).isdigit():raise CRMError('GENERATION_ACTOR_REQUIRED',403)
        user=db.get(Usuario,int(actor))
        if not user or not user.activo:raise CRMError('GENERATION_ACTOR_REQUIRED',403)
        yield service(SimpleNamespace(method='POST',query_params=QueryParams()),db,user)
