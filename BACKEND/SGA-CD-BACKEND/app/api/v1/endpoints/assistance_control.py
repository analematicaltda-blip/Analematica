"""Control plane: administrator JWT approvals and separate paired-device credentials."""
import json
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,Request
from pydantic import BaseModel,ConfigDict,Field
from typing import Literal
from app.api import deps
from app.models.assistance import ControlDevice,ControlJob,ControlApproval
from app.services.assistance import control
from app.core.rate_limiter import limiter
from fastapi.routing import APIRoute

class PrivateRoute(APIRoute):
    def get_route_handler(self):
        handler=super().get_route_handler()
        async def private(request):
            response=await handler(request)
            response.headers['Cache-Control']='no-store'
            response.headers['Pragma']='no-cache'
            return response
        return private

def rate_limit(resource,maximum,window):
    async def check(request:Request):
        # Do not trust forwarded headers supplied to a public pairing endpoint.
        peer=request.client.host if request.client else 'unknown'
        limited,retry=limiter.is_rate_limited('control:'+resource+':'+peer,maximum,window)
        if limited:raise HTTPException(429,'Demasiadas solicitudes de vinculación.',headers={'Retry-After':str(retry)})
    return check

router=APIRouter(route_class=PrivateRoute)
class Body(BaseModel):model_config=ConfigDict(extra='forbid')
class Pair(Body):platforms:list[Literal['meta','tiktok','gmail','youtube']]=Field(min_length=1,max_length=4)
class Claim(Body):
    pairing_code:str=Field(min_length=16,max_length=32)
    name:str=Field(min_length=1,max_length=80)
    kind:Literal['desktop','android','ios']='desktop'
class Job(Body):
    device_id:UUID
    platform:Literal['meta','tiktok','gmail','youtube']
    account_label:Literal['principal']='principal'
    operation:Literal['browser_open','browser_snapshot','browser_click','browser_fill','browser_press','browser_upload','files_list','desktop_status','mobile_launch','mobile_snapshot','mobile_tap','mobile_type','mobile_swipe','mobile_open_url']
    arguments:dict=Field(default_factory=dict)
    purpose:str=Field(min_length=5,max_length=300)
class Approval(Body):
    stage:int=Field(ge=1,le=3)
    digest:str=Field(pattern=r'^[a-f0-9]{64}$')
    confirmation:str=Field(min_length=10,max_length=100)
class Report(Body):
    lease_id:str=Field(pattern=r'^[a-f0-9]{48}$')
    outcome:Literal['delivered','not_delivered','uncertain']
    data:dict=Field(default_factory=dict)

def administrator(db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)):
    from app.services.assistance.engine import Actor
    return control.require_staff(db,Actor(user.id,user.inquilino_id))

def paired(request:Request,db=Depends(deps.get_db)):
    header=request.headers.get('Authorization','')
    if not header.startswith('Bearer '):raise HTTPException(401,'Falta la credencial del equipo.')
    return control.authenticate_device(db,header[7:])

@router.get('/policy')
def policy(who=Depends(administrator)):
    return {**control.POLICY_DATA,'same_requesting_administrator':True,'pairing_counts_as_execution_approval':False,'automatic_approvals':False}

@router.post('/pairings',status_code=201,dependencies=[Depends(rate_limit('control_pairing',10,60))])
def pair(body:Pair,db=Depends(deps.get_db),who=Depends(administrator)):
    return control.pair(db,who,body.platforms)

@router.post('/claim',status_code=201,dependencies=[Depends(rate_limit('control_claim',10,60))])
def claim(body:Claim,db=Depends(deps.get_db)):
    return control.claim(db,body.pairing_code,body.name,body.kind)

@router.get('/devices')
def devices(db=Depends(deps.get_db),who=Depends(administrator)):
    rows=db.query(ControlDevice).filter_by(user_id=who.user_id,tenant_id=who.tenant_id).all()
    return {'devices':[{'id':r.id,'name':r.name,'kind':r.kind,'platforms':json.loads(r.scopes),'revoked':bool(r.revoked),'last_seen':r.last_seen} for r in rows]}

@router.post('/devices/{identifier}/revoke')
def revoke(identifier:UUID,db=Depends(deps.get_db),who=Depends(administrator)):
    return control.revoke(db,who,str(identifier))

@router.post('/jobs',status_code=201)
def job(body:Job,db=Depends(deps.get_db),who=Depends(administrator)):
    return control.create_job(db,who,str(body.device_id),body.platform,body.account_label,body.operation,body.arguments,body.purpose)

@router.get('/jobs')
def jobs(db=Depends(deps.get_db),who=Depends(administrator)):
    rows=db.query(ControlJob).filter_by(user_id=who.user_id,tenant_id=who.tenant_id).order_by(ControlJob.expires_at.desc()).limit(30).all()
    return {'jobs':[control.view(row) for row in rows]}

@router.get('/jobs/{identifier}')
def get_job(identifier:UUID,db=Depends(deps.get_db),who=Depends(administrator)):
    row=control.job_owned(db,who,str(identifier));result=control.view(row)
    result['authorization_history']=[{'stage':a.stage,'user_id':a.user_id,'digest':a.digest,'created_at':a.created_at} for a in db.query(ControlApproval).filter_by(job_id=row.id).order_by(ControlApproval.stage)]
    return result

@router.post('/jobs/{identifier}/authorize')
def approve(identifier:UUID,body:Approval,db=Depends(deps.get_db),who=Depends(administrator)):
    return control.approve(db,who,str(identifier),body.stage,body.digest,body.confirmation)

@router.post('/jobs/{identifier}/stop')
def stop(identifier:UUID,db=Depends(deps.get_db),who=Depends(administrator)):
    return control.stop(db,who,str(identifier))

@router.get('/device/queue')
def queue(device=Depends(paired),db=Depends(deps.get_db)):
    rows=db.query(ControlJob).filter_by(device_id=device.id,status='approved',stop_requested=0).filter(ControlJob.expires_at>=control.now()).order_by(ControlJob.expires_at).limit(5).all()
    return {'jobs':[{'id':r.id} for r in rows],'policy':control.POLICY}

@router.post('/device/jobs/{identifier}/begin')
def begin(identifier:UUID,device=Depends(paired),db=Depends(deps.get_db)):
    return control.begin(db,device,str(identifier))

@router.post('/device/jobs/{identifier}/result')
def report(identifier:UUID,body:Report,device=Depends(paired),db=Depends(deps.get_db)):
    return control.report(db,device,str(identifier),body.lease_id,body.outcome,body.data)
