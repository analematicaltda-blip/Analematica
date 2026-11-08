"""Editorial review API. Deliberately has no publishing endpoint."""
from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import Field
from sqlalchemy.orm import Session
from app.api import deps
from app.api.v1.endpoints.assistance import Body, actor
from app.core.rate_limiter import rate_limit
from app.services.assistance import content

router = APIRouter()

class Draft(Body):
    platform: Literal['meta', 'tiktok', 'gmail', 'youtube']
    brief: str = Field(min_length=3, max_length=4000)
    text: str = Field(min_length=1, max_length=12000)

class Revision(Draft):
    revision: int = Field(ge=1)

class Review(Body):
    revision: int = Field(ge=1)
    digest: str = Field(pattern=r'^[a-f0-9]{64}$')
    accuracy_rights_privacy_checked: bool

class Generation(Body):
    platform: Literal['meta', 'tiktok', 'gmail', 'youtube']
    brief: str = Field(min_length=3, max_length=4000)
    model: str = Field(min_length=1, max_length=100)
    share_with_local_model: bool = False

@router.post('/drafts', status_code=201)
def create(body: Draft, db: Session = Depends(deps.get_db), who=Depends(actor)):
    return content.create(db, who, body.platform, body.brief, body.text)

@router.get('/drafts/{identifier}')
def get(identifier: UUID, db: Session = Depends(deps.get_db), who=Depends(actor)):
    return content.view(content.owned(db, who, str(identifier)))

@router.put('/drafts/{identifier}')
def revise(identifier: UUID, body: Revision, db: Session = Depends(deps.get_db), who=Depends(actor)):
    return content.revise(db, who, str(identifier), body.revision, body.platform, body.brief, body.text)

@router.post('/drafts/{identifier}/review')
def review(identifier: UUID, body: Review, db: Session = Depends(deps.get_db), who=Depends(actor)):
    return content.review(db, who, str(identifier), body.revision, body.digest, body.accuracy_rights_privacy_checked)

@router.get('/drafts/{identifier}/export')
def export(identifier: UUID, db: Session = Depends(deps.get_db), who=Depends(actor)):
    return content.export(db, who, str(identifier))

@router.post('/generate', status_code=201, dependencies=[Depends(rate_limit('content_generate', 3, 60))])
async def generate(body: Generation, db: Session = Depends(deps.get_db), who=Depends(actor)):
    content.enabled(db, who)
    text, source = await content.generate(body.platform + '\n' + body.brief, body.model, body.share_with_local_model)
    return content.create(db, who, body.platform, body.brief, text, source)

@router.get('/drafts')
def drafts(db: Session = Depends(deps.get_db), who=Depends(actor)):
    content.enabled(db, who)
    from app.models.assistance import ContentDraft
    rows = db.query(ContentDraft).filter_by(user_id=who.user_id, tenant_id=who.tenant_id).order_by(ContentDraft.created_at.desc(), ContentDraft.id).limit(50).all()
    return {'drafts': [{'id': row.id, 'revision': row.revision, 'status': row.status} for row in rows], 'limit': 50}
