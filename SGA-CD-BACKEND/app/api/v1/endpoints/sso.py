from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.api import deps
from app import crud
from app.core import security
from app.core.rate_limiter import rate_limit
from app.services import sso_service as sso

router=APIRouter()
class FlowRequest(BaseModel):
    flow_id:str=Field(min_length=20,max_length=80)
    proof:str=Field(min_length=32,max_length=128)
    password:str=Field(min_length=1,max_length=200)

def failure(): return HTTPException(status_code=400,detail='Acceso no disponible, no autorizado o vencido. Intenta de nuevo.')

@router.get('/providers')
def providers():
    result={}
    for provider in sso.PROVIDERS:
        try: sso.provider_config(provider);result[provider]=True
        except sso.SSOError: result[provider]=False
    return result

@router.post('/{provider}/start',dependencies=[Depends(rate_limit('sso-start',max_requests=10,window_seconds=60))])
def start(provider:str,response:Response):
    response.headers["Cache-Control"]="no-store"
    try: return sso.start(provider)
    except sso.SSOError: raise HTTPException(503,'Proveedor de acceso todavía no configurado')

@router.get('/{provider}/authorize')
def authorize(provider:str,flow_id:str):
    try: url,cookie=sso.authorize(provider,flow_id)
    except sso.SSOError: raise failure()
    response=RedirectResponse(url,status_code=303)
    response.set_cookie('sga_sso_'+flow_id,cookie,max_age=300,secure=True,httponly=True,samesite='lax',path='/api/v1/sso/')
    response.headers['Cache-Control']='no-store'
    response.headers['Referrer-Policy']='no-referrer'
    return response

@router.get('/{provider}/callback')
def callback(provider:str,request:Request,state:str='',code:str='',error:str=''):
    import re
    flow_id=state.partition('.')[0]
    if not re.fullmatch(r'[A-Za-z0-9_-]{32}',flow_id): raise failure()
    cookie=request.cookies.get('sga_sso_'+flow_id,'')
    try:
        if error: raise sso.SSOError('Autorización cancelada')
        sso.callback(provider,state,code,cookie)
        message='Autorización completada. Regresa a la ventana de SGA-CD donde comenzaste.'
    except sso.SSOError:
        message='No se completó el acceso. Regresa a SGA-CD y comprueba que tu cuenta esté autorizada.'
    response=HTMLResponse('<!doctype html><html lang="es"><meta name="viewport" content="width=device-width"><title>Acceso SGA-CD</title><body style="margin:0;padding:48px 24px;background:#070B14;color:#38BDF8;font:18px system-ui"><h1>SGA-CD</h1><p>'+message+'</p></body></html>')
    response.delete_cookie('sga_sso_'+flow_id,path='/api/v1/sso/',secure=True,httponly=True,samesite='lax')
    response.headers.update({'Cache-Control':'no-store','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'"})
    return response

@router.post('/result')
def result(body:FlowRequest,response:Response,db:Session=Depends(deps.get_db)):
    response.headers["Cache-Control"]="no-store"
    def resolve(username,email):
        user=crud.user.get_user_by_username(db,username=username)
        if not user or not user.activo or (user.correo or '').lower()!=email: raise sso.SSOError('Cuenta no autorizada')
        if not security.verify_password(body.password,user.password_hash): raise sso.SSOError('Cuenta no autorizada')
        roles=getattr(user,'role_list',[])
        claims=dict(sub=str(user.id),roles=roles,inquilino_id=user.inquilino_id,nombre_completo=user.nombre_completo)
        return dict(status='authenticated',access_token=security.create_access_token(claims),refresh_token=security.create_refresh_token({'sub':str(user.id)}),token_type='bearer',user=dict(id=user.id,nombre=user.nombre_completo,email=user.correo,roles=roles,inquilino_id=user.inquilino_id))
    try: return sso.consume(body.flow_id,body.proof,resolve)
    except sso.SSOError: raise failure()
