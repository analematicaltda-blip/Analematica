"""Authenticated, tenant-bound user assistance. All external actions remain manual."""
import os
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.api import deps
from app.models.tenancy import Inquilino
from app.models.assistance import AssistanceSession, AssistanceEvent, AssistanceAdvice
from app.services.assistance import engine, duet
from app.core.rate_limiter import rate_limit

router = APIRouter()

class Body(BaseModel):
    model_config = ConfigDict(extra='forbid')

class Start(Body):
    workflow_id: str = Field(min_length=1,max_length=100)

class Advance(Body):
    revision: int = Field(ge=1)
    step_id: str = Field(min_length=1,max_length=100)
    checklist_checked: bool
    confirmed: bool = False

class Close(Body):
    revision: int = Field(ge=1)

class Question(Body):
    request_id: UUID
    question: str = Field(min_length=3,max_length=2000)
    share_with_open_duet: bool = False

def actor(db: Session = Depends(deps.get_db), user = Depends(deps.get_current_active_user)):
    tenant = db.get(Inquilino, user.inquilino_id) if user.inquilino_id else None
    if not user.activo or tenant is None or not tenant.activo:
        raise HTTPException(403, 'La asistencia requiere una cuenta y una organización activas.')
    return engine.Actor(user.id, tenant.id)

@router.get('/catalog')
def catalog(who=Depends(actor)):
    return engine.catalog()

@router.get('/capabilities')
def capabilities(who=Depends(actor)):
    enabled = os.environ.get('ASSISTANCE_DUET_ENABLED') == '1'
    assigned = os.environ.get('ASSISTANCE_DUET_USER_ID') == str(who.user_id) and os.environ.get('ASSISTANCE_DUET_TENANT_ID') == str(who.tenant_id)
    return {'mode':'guidance_only', 'external_execution':False, 'platforms':['meta','tiktok','gmail','youtube'],
        'open_duet': 'configured_not_live_verified' if enabled and assigned else 'not_connected',
        'desktop':'paired_companion_requires_signed_authorizations', 'desktop_connected_to_this_server':False,
        'control_api':'/api/v1/assistance/control', 'minimum_authorizations':2, 'mutation_authorizations':3, 'same_requesting_administrator':True,
        'observation':'requires_pairing_local_runner_and_separate_authorizations', 'provider_authorizations':'not_granted_by_installation'}

@router.post('/sessions', status_code=201)
def start(body: Start, db: Session=Depends(deps.get_db), who=Depends(actor)):
    return engine.create(db, who, body.workflow_id)

@router.get('/sessions')
def sessions(db: Session=Depends(deps.get_db), who=Depends(actor)):
    rows = db.query(AssistanceSession).filter_by(user_id=who.user_id, tenant_id=who.tenant_id).order_by(AssistanceSession.created_at.desc()).limit(50).all()
    return {'sessions':[engine.state(row) for row in rows]}

@router.get('/sessions/{identifier}')
def get(identifier: UUID, db: Session=Depends(deps.get_db), who=Depends(actor)):
    return engine.state(engine.owned(db, who, str(identifier)))

@router.post('/sessions/{identifier}/advance')
def advance(identifier: UUID, body: Advance, db: Session=Depends(deps.get_db), who=Depends(actor)):
    return engine.advance(db, who, str(identifier), body.revision, body.step_id, body.checklist_checked, body.confirmed)

@router.post('/sessions/{identifier}/close')
def close(identifier: UUID, body: Close, db: Session=Depends(deps.get_db), who=Depends(actor)):
    return engine.close(db, who, str(identifier), body.revision)

@router.get('/sessions/{identifier}/events')
def events(identifier: UUID, db: Session=Depends(deps.get_db), who=Depends(actor)):
    engine.owned(db, who, str(identifier))
    rows = db.query(AssistanceEvent).filter_by(session_id=str(identifier),user_id=who.user_id,tenant_id=who.tenant_id).order_by(AssistanceEvent.id).limit(100).all()
    return {'verification':'user_reported', 'events':[{'step_id':row.step_id,'event':row.event} for row in rows]}

@router.post('/sessions/{identifier}/advice', dependencies=[Depends(rate_limit('assistance_advice',10,60))])
async def advice(identifier: UUID, body: Question, db: Session=Depends(deps.get_db), who=Depends(actor)):
    row = engine.owned(db, who, str(identifier))
    if row.status != 'active':
        raise HTTPException(409, 'La guía no tiene un paso activo.')
    if not body.share_with_open_duet:
        raise HTTPException(409, 'Autoriza compartir solo esta pregunta y el paso actual con tu Open Duet.')
    duet.owner_allowed(who)
    old = db.get(AssistanceAdvice, str(body.request_id))
    if old:
        if old.user_id != who.user_id or old.tenant_id != who.tenant_id or old.session_id != str(identifier):
            raise HTTPException(404, 'Consulta no encontrada.')
        return {'id':old.id,'status':old.status}
    client = duet.DuetClient.configured()
    snapshot = engine.state(row)
    job = AssistanceAdvice(id=str(body.request_id), session_id=str(identifier), user_id=who.user_id,
        tenant_id=who.tenant_id, source_revision=row.revision, status='preparing')
    try:
        db.add(job)
        db.commit()
    except IntegrityError:
        db.rollback()
        await client.close()
        raise HTTPException(409, 'Esta consulta ya se está preparando. Recarga su estado.') from None
    try:
        job.agent_id, job.thread_id, job.turn_id = await client.advise(snapshot, body.question)
        job.status = 'running'
        db.commit()
    except HTTPException:
        job.status = 'uncertain'
        db.commit()
        raise
    finally:
        await client.close()
    return {'id':job.id,'status':job.status}

@router.get('/sessions/{identifier}/advice/{question_id}')
async def answer(identifier: UUID, question_id: UUID, db: Session=Depends(deps.get_db), who=Depends(actor)):
    engine.owned(db, who, str(identifier))
    job = db.query(AssistanceAdvice).filter_by(id=str(question_id),session_id=str(identifier),user_id=who.user_id,tenant_id=who.tenant_id).first()
    if job is None:
        raise HTTPException(404, 'Consulta no encontrada.')
    if job.status not in {'running','succeeded'}:
        return {'id':job.id,'status':job.status,'answer':None}
    duet.owner_allowed(who)
    client = duet.DuetClient.configured()
    try:
        result = await client.result(job.thread_id, job.turn_id)
    finally:
        await client.close()
    job.status = result['status']
    db.commit()
    return {'id':job.id,**result}

from app.api.v1.endpoints import assistance_control
router.include_router(assistance_control.router,prefix='/control',tags=['Authorized desktop control'])

from app.api.v1.endpoints import resources
router.include_router(resources.router,prefix="/resources",tags=["Administrative security and AI resources"])
