"""Authenticated Meta Ads setup, OAuth and reads. No live-ad mutation endpoints."""
import json
import re
import uuid
from decimal import Decimal
from typing import Literal
from urllib.parse import urlsplit, parse_qs
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError, UUID4
from sqlalchemy.exc import IntegrityError
from app.api import deps
from app.models.advertising import MetaAdsAuthorization, MetaAdsOAuthState, AdvertisingProfile, AdvertisingDraft
from app.services import meta_ads_service as ads

router=APIRouter()
class Body(BaseModel): model_config=ConfigDict(extra='forbid')
class AppConfig(Body):
    app_id:str=Field(pattern=r'^\d{1,40}$')
    client_secret:SecretStr|None=None
    api_version:str=Field(default=ads.GRAPH_VERSION,pattern=r'^v\d{1,2}\.\d$')
    login_config_id:str=Field(default='',pattern=r'^\d{0,40}$')
    redirect_uris:list[str]=Field(min_length=1,max_length=5)
class OAuthStart(Body):
    redirect_uri:str=Field(max_length=500)
    return_path:Literal['/admin.html#tab-meta-ads','/app.html#/admin_empresa/full/canales','/sga/app.html#/admin_empresa/full/canales']='/admin.html#tab-meta-ads'
class Selection(Body): account_id:str=Field(pattern=r'^act_\d{1,40}$')
class Profile(Body): public_url:str=Field(max_length=400);declared_id:str=Field(default='',pattern=r'^\d{0,40}$')
class Draft(Body):
    request_id:UUID4
    title:str=Field(min_length=1,max_length=100)
    description:str=Field(default='',max_length=2000)
    objective:Literal['OUTCOME_AWARENESS','OUTCOME_TRAFFIC','OUTCOME_ENGAGEMENT','OUTCOME_LEADS','OUTCOME_SALES','OUTCOME_APP_PROMOTION']='OUTCOME_TRAFFIC'
    planned_budget:Decimal|None=Field(default=None,gt=0,le=100000000)
    currency:str|None=Field(default=None,pattern=r'^[A-Z]{3}$')

def context(db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)): return ads.actor_for(db,user)
def cookie_name(state): return 'sgacd_meta_'+ads.digest(state or '')[:16]

@router.get('/status')
def status(response:Response,db=Depends(deps.get_db),actor=Depends(context)):
    response.headers['Cache-Control']='no-store'
    return ads.status(db,actor)

@router.put('/app')
async def configure(request:Request,db=Depends(deps.get_db),actor=Depends(context)):
    if not actor.owner:raise HTTPException(403,'Solo el dueño configura la aplicación compartida.')
    try:body=AppConfig.model_validate(await request.json())
    except (ValueError,ValidationError):raise HTTPException(422,'Completa los campos de la aplicación. No se devolvieron secretos.') from None
    return ads.configure_app(db,actor,body)

@router.post('/oauth/start')
def start(body:OAuthStart,response:Response,db=Depends(deps.get_db),actor=Depends(context)):
    result=ads.start_oauth(db,actor,body.redirect_uri,body.return_path)
    response.set_cookie(cookie_name(result['state']),result['browser'],max_age=600,httponly=True,secure=result['secure'],samesite='lax',path=ads.CALLBACK)
    response.headers['Cache-Control']='no-store'
    return {'authorization_url':result['authorization_url'],'expires_in':600}

@router.get('/oauth/callback')
def callback(request:Request,state:str|None=None,code:str|None=None,error:str|None=None,db=Depends(deps.get_db)):
    # Uvicorn logs the scope at response start: remove authorization code/query now.
    request.scope['query_string']=b''
    browser=request.cookies.get(cookie_name(state))
    path,success=ads.finish_oauth(db,state,browser,code,denied=bool(error))
    destination=path.split('#')[0]+('?meta=connected' if success else '?meta=failed')+('#'+path.split('#',1)[1] if '#' in path else '')
    response=RedirectResponse(destination,status_code=303)
    response.delete_cookie(cookie_name(state),path=ads.CALLBACK)
    response.headers['Cache-Control']='no-store';response.headers['Referrer-Policy']='no-referrer'
    return response

@router.get('/accounts')
def accounts(cursor:str|None=Query(default=None,max_length=2048),db=Depends(deps.get_db),actor=Depends(context)):return ads.accounts(db,actor,cursor)

@router.put('/account')
def select(body:Selection,db=Depends(deps.get_db),actor=Depends(context)):return ads.select_account(db,actor,body.account_id)

@router.get('/campaigns')
def campaigns(cursor:str|None=Query(default=None,max_length=2048),db=Depends(deps.get_db),actor=Depends(context)):return ads.campaigns(db,actor,cursor)

@router.get('/insights')
def insights(preset:Literal['today','yesterday','last_7d','last_30d']='last_7d',db=Depends(deps.get_db),actor=Depends(context)):return ads.insights(db,actor,preset)

@router.post('/profiles/verify')
def verify(db=Depends(deps.get_db),actor=Depends(context)):
    ads.manager(actor);return ads.verify_profiles(db,actor)

@router.put('/profiles/{network}')
def profile(network:Literal['facebook','instagram','x'],body:Profile,db=Depends(deps.get_db),actor=Depends(context)):
    ads.manager(actor)
    try:p=urlsplit(body.public_url)
    except ValueError:raise HTTPException(422,'URL de perfil no válida.') from None
    allowed={'facebook':['facebook.com','www.facebook.com'],'instagram':['instagram.com','www.instagram.com'],'x':['x.com','www.x.com']}
    try:port=p.port
    except ValueError:raise HTTPException(422,'URL de perfil no válida.') from None
    if p.scheme!='https' or p.hostname not in allowed[network] or p.username or p.password or p.fragment or port is not None or any(ord(c)<32 for c in body.public_url):raise HTTPException(422,'Usa una URL HTTPS del perfil en la plataforma elegida.')
    handle=p.path.strip('/').split('/')[0] if network!='facebook' else ''
    if network!='facebook' and not re.fullmatch(r'[A-Za-z0-9_.]{1,80}',handle):raise HTTPException(422,'Identificador de perfil no válido.')
    declared_id=body.declared_id
    if network=='facebook' and p.path=='/profile.php':
        candidate=parse_qs(p.query).get('id',[''])[0]
        if not re.fullmatch(r'\d{1,40}',candidate):raise HTTPException(422,'El enlace de Facebook no contiene un identificador válido.')
        if declared_id and declared_id!=candidate:raise HTTPException(422,'El identificador no coincide con el enlace de Facebook.')
        declared_id=candidate
    row=db.query(AdvertisingProfile).filter_by(scope=actor.scope,network=network).first()
    if not row:row=AdvertisingProfile(scope=actor.scope,network=network,public_url=body.public_url);db.add(row)
    row.public_url=body.public_url;row.handle=handle;row.declared_id=declared_id;row.verified_id=None;row.verified_at=None;db.commit()
    return {'saved':True,'profiles':ads.profiles(db,actor.scope)}

@router.delete('/authorization')
def forget(db=Depends(deps.get_db),actor=Depends(context)):
    ads.manager(actor);row=db.get(MetaAdsAuthorization,actor.scope)
    if row:db.delete(row)
    for state in db.query(MetaAdsOAuthState).filter_by(scope=actor.scope,used_at=None):state.used_at=ads.now();state.outcome='disconnected'
    for p in db.query(AdvertisingProfile).filter_by(scope=actor.scope):
        if p.network in ['facebook','instagram']:p.verified_id=None;p.verified_at=None
    db.commit();return {'disconnected_locally':True,'meta_campaigns_changed':False}

def draft_data(row):
    return {'id':row.id,'title':row.title,'description':row.description,'objective':row.objective,'account_id':row.account_id,'planned_budget':row.planned_budget,'currency':row.currency,'status':row.status,'submitted_to_meta':False,'created_at':row.created_at.isoformat() if row.created_at else None}

@router.get('/drafts')
def drafts(db=Depends(deps.get_db),actor=Depends(context)):
    return {'drafts':[draft_data(r) for r in db.query(AdvertisingDraft).filter_by(scope=actor.scope).order_by(AdvertisingDraft.created_at.desc()).limit(100)]}

@router.post('/drafts',status_code=201)
def draft(body:Draft,db=Depends(deps.get_db),actor=Depends(context)):
    key=str(body.request_id);fingerprint=ads.digest(json.dumps(body.model_dump(mode='json',exclude={'request_id'}),sort_keys=True));row=db.get(AdvertisingDraft,key)
    if row:
        if row.scope!=actor.scope:raise HTTPException(404,'Borrador no encontrado en tu organización.')
        if row.request_hash!=fingerprint:raise HTTPException(409,'La referencia corresponde a otro borrador.')
        return draft_data(row)
    if not body.title.strip():raise HTTPException(422,'Escribe el nombre del borrador.')
    auth=db.get(MetaAdsAuthorization,actor.scope);account=json.loads(auth.account) if auth else {}
    if body.planned_budget is not None and (not account or not body.currency or account.get('currency')!=body.currency):raise HTTPException(422,'Antes de indicar presupuesto selecciona una cuenta y usa su moneda real.')
    row=AdvertisingDraft(id=key,request_hash=fingerprint,scope=actor.scope,title=body.title.strip(),description=body.description,objective=body.objective,account_id=account.get('id'),planned_budget=str(body.planned_budget) if body.planned_budget else None,currency=account.get('currency'),status='local_draft',created_by=actor.user.id)
    db.add(row)
    try:db.commit()
    except IntegrityError:
        db.rollback()
        if not db.get(AdvertisingDraft,key):raise HTTPException(409,'No se confirmó el guardado del borrador.') from None
        return draft(body,db,actor)
    return draft_data(row)
