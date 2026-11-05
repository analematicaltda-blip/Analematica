"""Instagram system-user consent; never return credentials to the browser."""
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field
from app.api import deps
from app.api.v1.endpoints.meta_ads import context
from app.services import instagram_service as instagram
from app.services import meta_ads_service as meta

router=APIRouter()
class Body(BaseModel):model_config=ConfigDict(extra='forbid')
class Config(Body):config_id:str=Field(pattern=r'^\d{1,40}$')
class Start(Body):redirect_uri:str=Field(max_length=500)
class Account(Body):account_id:str=Field(pattern=r'^\d{1,40}$')

def owner(actor=Depends(context)):
    if not actor.owner:raise HTTPException(403,'Este conector inicial se configura desde la consola del dueño.')
    return actor

def cookie(state):return 'sgacd_ig_'+meta.digest(state or '')[:16]

@router.get('/status')
def status(response:Response,db=Depends(deps.get_db),actor=Depends(owner)):
    response.headers['Cache-Control']='no-store'
    return instagram.status(db,actor)

@router.put('/config')
def configure(body:Config,db=Depends(deps.get_db),actor=Depends(owner)):
    return instagram.configure(db,actor,body.config_id)

@router.post('/oauth/start')
def start(body:Start,response:Response,db=Depends(deps.get_db),actor=Depends(owner)):
    result=instagram.start(db,actor,body.redirect_uri)
    response.set_cookie(cookie(result['state']),result['browser'],max_age=600,httponly=True,secure=result['secure'],samesite='lax',path=instagram.CALLBACK)
    response.headers['Cache-Control']='no-store'
    return {'authorization_url':result['authorization_url']}

@router.get('/oauth/callback')
def callback(request:Request,state:str|None=None,code:str|None=None,error:str|None=None,db=Depends(deps.get_db)):
    request.scope['query_string']=b''
    success=instagram.finish(db,state,request.cookies.get(cookie(state)),code,bool(error))
    response=RedirectResponse('/admin.html?instagram='+('connected' if success else 'failed')+'#tab-meta-ads',status_code=303)
    response.delete_cookie(cookie(state),path=instagram.CALLBACK)
    response.headers['Cache-Control']='no-store';response.headers['Referrer-Policy']='no-referrer'
    return response

@router.put('/account')
def select_account(body:Account,db=Depends(deps.get_db),actor=Depends(owner)):
    return instagram.select_account(db,actor,body.account_id)
