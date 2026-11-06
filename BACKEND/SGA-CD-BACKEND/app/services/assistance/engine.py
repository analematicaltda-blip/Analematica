import copy
from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
import uuid
from fastapi import HTTPException
from sqlalchemy import update
from app.models.assistance import AssistanceSession, AssistanceEvent

@dataclass(frozen=True)
class Actor:
    user_id: int
    tenant_id: int

@lru_cache(maxsize=1)
def _catalog():
    return json.loads(Path(__file__).with_name('catalog.json').read_text())

def catalog():
    return copy.deepcopy(_catalog())

def workflow(identifier):
    item = next((item for item in _catalog()['workflows'] if item['id'] == identifier), None)
    if item is None:
        raise HTTPException(404, 'Guía no encontrada.')
    return copy.deepcopy(item)

def owned(db, actor, identifier):
    row = db.query(AssistanceSession).filter_by(id=identifier, user_id=actor.user_id, tenant_id=actor.tenant_id).first()
    if row is None:
        raise HTTPException(404, 'Sesión no encontrada.')
    return row

def state(row):
    guide = json.loads(row.workflow_snapshot)
    steps = guide['steps']
    return {'id':row.id, 'workflow_id':row.workflow_id, 'title':guide['title'], 'platform':guide['platform'],
            'catalog_version':row.catalog_version, 'position':row.position, 'total':len(steps),
            'revision':row.revision, 'status':row.status, 'entry_url':guide['entry_url'], 'references':guide['references'],
            'current_step':steps[row.position] if row.status == 'active' and row.position < len(steps) else None,
            'mode':'guidance_only', 'external_execution':False, 'verification':'user_reported'}

def create(db, actor, identifier):
    guide = workflow(identifier)
    row = AssistanceSession(id=str(uuid.uuid4()), user_id=actor.user_id, tenant_id=actor.tenant_id,
        workflow_id=identifier, catalog_version=_catalog()['version'], workflow_snapshot=json.dumps(guide, ensure_ascii=False),
        position=0, revision=1, status='active')
    db.add(row)
    db.commit()
    return state(row)

def advance(db, actor, identifier, revision, step_id, checklist_checked, confirmed):
    row = owned(db, actor, identifier)
    if row.revision != revision or row.status != 'active':
        raise HTTPException(409, 'La guía cambió o ya terminó. Recarga su estado.')
    guide = json.loads(row.workflow_snapshot)
    step = guide['steps'][row.position]
    if step_id != step['id']:
        raise HTTPException(409, 'Solo puedes completar el paso actual.')
    if not checklist_checked:
        raise HTTPException(422, 'Revisa la lista del paso antes de continuar.')
    if step['requires_confirmation'] and not confirmed:
        raise HTTPException(409, 'Confirma la revisión y realiza tú la acción en la plataforma. El asistente no la ejecuta.')
    position = row.position + 1
    changed = db.execute(update(AssistanceSession).where(AssistanceSession.id == row.id,
        AssistanceSession.revision == revision, AssistanceSession.status == 'active',
        AssistanceSession.user_id == actor.user_id, AssistanceSession.tenant_id == actor.tenant_id)
        .values(position=position, revision=revision + 1, status='completed' if position == len(guide['steps']) else 'active'))
    if changed.rowcount != 1:
        db.rollback()
        raise HTTPException(409, 'Otro dispositivo actualizó la guía. Recarga su estado.')
    db.add(AssistanceEvent(session_id=row.id, user_id=actor.user_id, tenant_id=actor.tenant_id,
        step_id=step_id, event='manual_action_reported' if step['requires_confirmation'] else 'step_reported_done'))
    db.commit()
    db.expire_all()
    return state(owned(db, actor, identifier))

def close(db, actor, identifier, revision):
    row = owned(db, actor, identifier)
    result = db.execute(update(AssistanceSession).where(AssistanceSession.id == row.id,
        AssistanceSession.revision == revision, AssistanceSession.status == 'active',
        AssistanceSession.user_id == actor.user_id, AssistanceSession.tenant_id == actor.tenant_id)
        .values(status='closed', revision=revision + 1))
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(409, 'La guía cambió o ya está cerrada.')
    db.add(AssistanceEvent(session_id=row.id, user_id=actor.user_id, tenant_id=actor.tenant_id,
        step_id='session', event='guide_closed_only'))
    db.commit()
    db.expire_all()
    return state(owned(db, actor, identifier))
