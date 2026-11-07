"""Read-only administrative discovery and explicit minimized audit download."""
from fastapi import APIRouter,Depends,Query
from typing import Literal
from app.api import deps
from app.api.v1.endpoints.assistance_control import administrator,PrivateRoute
from app.services.resources import catalog,security

router=APIRouter(route_class=PrivateRoute)
Category=Literal['text','image','transcription','speech','embeddings','vision','video','music','translation','extraction','code','search','moderation','hosting','multimodal']

@router.get('/providers')
def providers(category:Category|None=None,q:str=Query(default='',max_length=100),local_only:bool=False,who=Depends(administrator)):
    return catalog.discover(category,q,local_only)

@router.get('/security/status')
def security_status(who=Depends(administrator)):
    return security.status()

@router.get('/security/control-audit-export')
def audit_export(after_id:int=Query(default=0,ge=0),limit:int=Query(default=100,ge=1,le=100),db=Depends(deps.get_db),who=Depends(administrator)):
    return security.export(db,who,after_id,limit)
