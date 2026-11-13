from contextlib import contextmanager
from types import SimpleNamespace
from starlette.datastructures import QueryParams
from app.db.session import SessionLocal
from app.models.user import Usuario
from .generation_models import GenerationJob
from .crm_api import service
from .crm import CRMError

def candidates():
    with SessionLocal() as db:
        return [(r.id,r.document) for r in db.query(GenerationJob).filter_by(status='QUEUED').order_by(GenerationJob.id).limit(100)]
@contextmanager
def context(document):
    with SessionLocal() as db:
        actor=document.get('creator_ref') if isinstance(document,dict) else None
        if not str(actor).isdigit():raise CRMError('GENERATION_ACTOR_REQUIRED',403)
        user=db.get(Usuario,int(actor))
        if not user or not user.activo:raise CRMError('GENERATION_ACTOR_REQUIRED',403)
        yield service(SimpleNamespace(method='POST',query_params=QueryParams()),db,user)
