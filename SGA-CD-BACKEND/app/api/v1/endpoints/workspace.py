"""First-party panels: JWT + active tenant + plan + delegation, never a browser worker key."""
import json
import uuid
from fastapi import APIRouter,Depends,HTTPException,Request
from fastapi.responses import Response
from pydantic import BaseModel,Field,SecretStr,ValidationError,EmailStr
from typing import Literal
from sqlalchemy import update
from app.api import deps
from app.models.user import Usuario
from app.models.workspace import WorkspaceGrant,WorkspaceAsset,WorkspaceLead,WorkspaceChannel
from app.services import workspace_service as ws
from app.services.plan_capability_service import FULL_QUOTAS

router=APIRouter()
class Body(BaseModel):model_config={'extra':'forbid'}
class Prompt(Body):prompt:str=Field(min_length=1,max_length=6000)
class Reel(Body):
    title:str=Field(min_length=1,max_length=90)
    caption:str=Field(default='',max_length=220)
    duration:int=Field(default=4,ge=1,le=15)
    image_id:str|None=None
class Grant(Body):permissions:dict[Literal['crm','media','publish','inbox'],bool]
class Lead(Body):
    name:str=Field(min_length=1,max_length=150)
    email:EmailStr|Literal['']=''
    stage:Literal['nuevo','contactado','propuesta','ganado','cerrado']='nuevo'
    notes:str=Field(default='',max_length=2000)
class Draft(Body):
    asset_id:str
    title:str=Field(min_length=1,max_length=100)
    description:str=Field(default='',max_length=2000)
class Publish(Draft):
    made_for_kids:bool
    confirm_private:Literal[True]
class Channel(Body):
    label:str=Field(min_length=1,max_length=120)
    client_id:SecretStr
    client_secret:SecretStr
    refresh_token:SecretStr
class Provider(Body):
    api_key:SecretStr
    text_model:str=Field(default='gemini-2.5-flash',pattern=r'^[A-Za-z0-9._-]{1,120}$')
    image_model:str=Field(default='gemini-2.5-flash-image',pattern=r'^[A-Za-z0-9._-]{1,120}$')

def context(db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)):return ws.access_for(db,user)
def decoded(response):
    try:value=response.json()
    except ValueError:raise HTTPException(502,'Respuesta no válida del estudio.') from None
    if not isinstance(value,dict):raise HTTPException(502,'Respuesta no válida del estudio.')
    return value

def execute(db,access,key,body,path,save=None):
    reservation=ws.reserve(db,access,key)
    try:
        result=decoded(ws.worker(path,body))
        return save(result) if save else result
    except Exception:
        db.rollback();ws.release(db,reservation);raise

@router.get('/session')
def session(access=Depends(context)):
    return {'user':{'id':access.user.id,'name':access.user.nombre_completo or access.user.nombre_usuario,'roles':sorted(access.roles),'tenant_id':access.tenant.id},'organization':'SGA-CD · Plataforma' if access.owner else access.tenant.nombre_empresa,'scope':'platform' if access.owner else 'company','plan':'platform' if access.owner else access.caps.canonical_plan,'full_enabled':access.full,'subscription_status':access.caps.subscription_status,'permissions':access.permissions,'manage_team':access.manages_team,'manage_channels':access.manages_team,'quotas':dict(FULL_QUOTAS if access.owner else access.caps.monthly_limits)}

@router.get('/team')
def team(db=Depends(deps.get_db),access=Depends(context)):
    if not access.manages_team:raise HTTPException(403,'Solo el administrador puede habilitar a su equipo.')
    result=[]
    for user in db.query(Usuario).filter(Usuario.inquilino_id==access.tenant.id).all():
        roles=ws.roles_of(user)
        grants={row.permission:row.enabled for row in db.query(WorkspaceGrant).filter(WorkspaceGrant.tenant_id==access.tenant.id,WorkspaceGrant.user_id==user.id).all()}
        result.append({'id':user.id,'name':user.nombre_completo or user.nombre_usuario,'roles':sorted(roles),'active':user.activo,'delegable':bool(user.activo and roles&ws.TEAM_ROLES) and not roles&{'admin_general','admin_empresa'},'permissions':{name:bool(access.full and (roles&ws.TEAM_ROLES or roles&{'admin_empresa','admin_general'}) and grants.get(name,True)) for name in sorted(ws.PERMISSIONS)}})
    return {'members':result,'full_enabled':access.full}

@router.put('/team/{user_id}/permissions')
def permissions(user_id:int,body:Grant,db=Depends(deps.get_db),access=Depends(context)):
    if not access.manages_team:raise HTTPException(403,'Solo el administrador puede habilitar a su equipo.')
    if not access.full:raise HTTPException(402,'Los permisos CRM y multimedia requieren Plan Full.')
    user=db.query(Usuario).filter(Usuario.id==user_id,Usuario.inquilino_id==access.tenant.id).first()
    if not user:raise HTTPException(404,'Miembro no encontrado en tu empresa.')
    roles=ws.roles_of(user)
    if not user.activo or not roles&ws.TEAM_ROLES or roles&{'admin_general','admin_empresa'}:raise HTTPException(403,'Esta cuenta no admite delegación de funciones administrativas.')
    for name,enabled in body.permissions.items():
        grant=db.query(WorkspaceGrant).filter(WorkspaceGrant.tenant_id==access.tenant.id,WorkspaceGrant.user_id==user.id,WorkspaceGrant.permission==name).first()
        if not grant:grant=WorkspaceGrant(tenant_id=access.tenant.id,user_id=user.id,permission=name);db.add(grant)
        grant.enabled=enabled;grant.granted_by=access.user.id
    db.commit()
    return {'saved':True,'user_id':user.id}

@router.get('/studio/status')
def studio_status(access=Depends(context)):
    access.require('media')
    data=decoded(ws.worker('/status'))
    return {key:data.get(key) for key in ['node','gemini_key_configured','remote_inference_verified','text_model','image_model','reel_renderer','ai_video']}

@router.post('/studio/script')
def script(body:Prompt,db=Depends(deps.get_db),access=Depends(context)):
    access.require('media');data=execute(db,access,'llm_prompts',body.model_dump(),'/studio/script')
    return {'text':data.get('text',''),'provider':data.get('provider'),'model':data.get('model')}

@router.post('/studio/image')
def image(body:Prompt,db=Depends(deps.get_db),access=Depends(context)):
    access.require('media')
    return execute(db,access,'images',body.model_dump(),'/studio/image',lambda result:ws.save_asset(db,access,result,'image',body.prompt[:100]))

@router.post('/studio/reel')
def reel(body:Reel,db=Depends(deps.get_db),access=Depends(context)):
    access.require('media');payload=body.model_dump(exclude={'image_id'})
    if body.image_id:payload['image']=ws.asset_for(db,access,body.image_id,'image').filename
    return execute(db,access,'reels',payload,'/studio/reel',lambda result:ws.save_asset(db,access,result,'reel',body.title))

@router.get('/assets')
def assets(db=Depends(deps.get_db),access=Depends(context)):
    access.require_asset_access()
    return {'assets':[ws.asset_dict(row) for row in db.query(WorkspaceAsset).filter(WorkspaceAsset.scope==access.scope).order_by(WorkspaceAsset.created_at.desc()).limit(100).all()]}

@router.get('/assets/{asset_id}/download')
def download(asset_id:str,db=Depends(deps.get_db),access=Depends(context)):
    access.require_asset_access();row=ws.asset_for(db,access,asset_id);response=ws.worker('/artifacts/'+row.filename)
    if len(response.content)>40*1024*1024:raise HTTPException(502,'Archivo demasiado grande.')
    media={'image':'image/png','reel':'video/mp4','draft':'application/json'}[row.kind]
    return Response(response.content,media_type=media,headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Disposition':'attachment; filename="'+row.filename+'"'})

@router.get('/crm/leads')
def leads(db=Depends(deps.get_db),access=Depends(context)):
    access.require('crm')
    return {'leads':[{'id':row.id,'name':row.name,'email':row.email,'stage':row.stage,'notes':row.notes} for row in db.query(WorkspaceLead).filter(WorkspaceLead.scope==access.scope).order_by(WorkspaceLead.created_at.desc()).limit(200).all()]}

@router.post('/crm/leads',status_code=201)
def create_lead(body:Lead,db=Depends(deps.get_db),access=Depends(context)):
    access.require('crm');row=WorkspaceLead(id=str(uuid.uuid4()),scope=access.scope,created_by=access.user.id,**body.model_dump());db.add(row);db.commit();return {'id':row.id}

@router.put('/crm/leads/{lead_id}')
def edit_lead(lead_id:str,body:Lead,db=Depends(deps.get_db),access=Depends(context)):
    access.require('crm');row=db.query(WorkspaceLead).filter(WorkspaceLead.id==lead_id,WorkspaceLead.scope==access.scope).first()
    if not row:raise HTTPException(404,'Contacto no encontrado en tu espacio.')
    for key,value in body.model_dump().items():setattr(row,key,value)
    db.commit();return {'saved':True}

@router.get('/channels')
def channels(db=Depends(deps.get_db),access=Depends(context)):
    if not access.manages_team:access.require('publish')
    rows=db.query(WorkspaceChannel).filter(WorkspaceChannel.scope==access.scope).all()
    return {'channels':[{'provider':row.provider,'label':row.label,'connected':True} for row in rows]}

@router.put('/channels/youtube')
async def connect_youtube(request:Request,db=Depends(deps.get_db),access=Depends(context)):
    if not access.manages_team:raise HTTPException(403,'Solo el administrador configura las credenciales del canal.')
    access.require('publish')
    try:
        body=Channel.model_validate(await request.json());credentials={key:getattr(body,key).get_secret_value() for key in ['client_id','client_secret','refresh_token']}
        if any(not value.strip() for value in credentials.values()):raise ValueError()
    except (ValidationError,ValueError):raise HTTPException(422,'Completa las credenciales del canal; no se devolvieron sus valores.') from None
    row=db.query(WorkspaceChannel).filter(WorkspaceChannel.scope==access.scope,WorkspaceChannel.provider=='youtube').first()
    if not row:row=WorkspaceChannel(scope=access.scope,provider='youtube');db.add(row)
    row.label=body.label;row.encrypted_credentials=ws.encryption().encrypt(json.dumps(credentials).encode()).decode();row.connected_by=access.user.id;db.commit()
    return {'connected':True,'provider':'youtube','label':row.label,'verified':False}

@router.delete('/channels/youtube')
def disconnect_youtube(db=Depends(deps.get_db),access=Depends(context)):
    if not access.manages_team:raise HTTPException(403,'Solo el administrador desconecta el canal.')
    db.query(WorkspaceChannel).filter(WorkspaceChannel.scope==access.scope,WorkspaceChannel.provider=='youtube').delete();db.commit();return {'connected':False}

@router.post('/social/draft')
def social_draft(body:Draft,db=Depends(deps.get_db),access=Depends(context)):
    access.require('publish');asset=ws.asset_for(db,access,body.asset_id,'reel')
    result=decoded(ws.worker('/social/draft',{'filename':asset.filename,'title':body.title,'description':body.description,'platforms':['youtube']}))
    return ws.save_asset(db,access,result,'draft',body.title)

@router.post('/youtube/upload-private')
def publish(body:Publish,db=Depends(deps.get_db),access=Depends(context)):
    access.require('publish');asset=ws.asset_for(db,access,body.asset_id,'reel')
    credentials=ws.channel_credentials(db,access,'youtube')
    if asset.publish_video_id:return {'privacy':'private','video_id':asset.publish_video_id,'duplicate_prevented':True}
    claim=db.execute(update(WorkspaceAsset).where(WorkspaceAsset.id==asset.id,WorkspaceAsset.publish_status=='new').values(publish_status='sending').returning(WorkspaceAsset.id)).scalar_one_or_none();db.commit()
    if not claim:raise HTTPException(409,'Este envío está iniciado o pendiente de confirmar; no se repetirá automáticamente.')
    try:reservation=ws.reserve(db,access,'social_posts')
    except Exception:
        asset.publish_status='new';db.commit();raise
    payload={'filename':asset.filename,'title':body.title,'description':body.description,'made_for_kids':body.made_for_kids,'confirm_private':True,'workspace':access.scope,'youtube_client_id':credentials['client_id'],'youtube_client_secret':credentials['client_secret'],'youtube_refresh_token':credentials['refresh_token']}
    try:
        result=decoded(ws.worker('/internal/youtube/upload-private',payload))
        if result.get('privacy')!='private' or not result.get('video_id'):raise HTTPException(502,'No se pudo confirmar la privacidad del envío.')
    except Exception:
        asset.publish_status='unknown';db.commit();raise
    asset.publish_status='uploaded';asset.publish_video_id=result['video_id'];db.commit()
    return {'privacy':'private','video_id':asset.publish_video_id}

@router.get('/inbox/status')
def inbox(access=Depends(context),db=Depends(deps.get_db)):
    access.require('inbox')
    configured={row.provider for row in db.query(WorkspaceChannel).filter_by(scope=access.scope).all()}
    return {'channels':[{'provider':provider,'connected':False,'outbound_configured':provider in configured,'state':'pending_webhooks' if provider in configured else 'pending_authorization'} for provider in ['whatsapp','instagram','facebook']],'automatic_replies':False,'message':'Las campañas usan las cuentas de salida configuradas. La bandeja de entrada y las respuestas requieren autorización y webhooks propios; no se muestran conversaciones simuladas.'}

@router.put('/providers/gemini')
async def configure_provider(request:Request,access=Depends(context)):
    if not access.owner:raise HTTPException(403,'Solo el administrador general configura el proveedor compartido.')
    try:
        body=Provider.model_validate(await request.json())
        if not body.api_key.get_secret_value().strip():raise ValueError()
    except (ValidationError,ValueError):raise HTTPException(422,'Configuración no válida; no se devolvieron credenciales.') from None
    decoded(ws.worker('/internal/providers/gemini',{'api_key':body.api_key.get_secret_value(),'text_model':body.text_model,'image_model':body.image_model},method='PUT'))
    return {'configured':True,'verified':False}

# Integrated campaign studio shares the exact same JWT, plan and tenant context.
from app.api.v1.endpoints import campaigns as integrated_campaigns
router.include_router(integrated_campaigns.router,prefix='/campaigns',tags=['Campaign calendar'])

from app.api.v1.endpoints import institutional as institutional_panels
router.include_router(institutional_panels.router,prefix='/institutional',tags=['Institutional role panels'])

from app.api.v1.endpoints import corporate as corporate_landing
router.include_router(corporate_landing.router,prefix="/corporate",tags=["Analematica"])
