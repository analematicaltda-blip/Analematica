"""Full-only campaigns: own channels, opted-in audience and explicit scheduling approval."""
from datetime import datetime,timedelta
import json
import hashlib
import re
import uuid
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from fastapi import APIRouter,Depends,HTTPException,Request
from fastapi.responses import Response,HTMLResponse
from pydantic import BaseModel,Field,SecretStr,ValidationError,EmailStr,TypeAdapter,UUID4
from typing import Literal
from app.api import deps

from app.models.workspace import WorkspaceChannel
from app.models.campaigns import Campaign,CampaignTarget,CampaignContact,CampaignScheduler,CampaignSetting
from app.models.billing import ConsumoInquilino
from app.services import workspace_service as ws
from app.services import campaign_service as cs

router=APIRouter()
def context(db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)):return ws.access_for(db,user)
class Body(BaseModel):model_config={'extra':'forbid'}
class Contact(Body):
    provider:Literal['whatsapp','gmail']
    address:str=Field(min_length=3,max_length=254)
    name:str=Field(default='',max_length=150)
    consent_source:str=Field(min_length=5,max_length=250)
    subscribed:Literal[True]
class Audience(Body):contacts:list[Contact]=Field(min_length=1,max_length=100)
class Subscription(Body):subscribed:bool
class Connection(Body):
    label:str=Field(min_length=1,max_length=120)
    credentials:dict[str,SecretStr]
class Adapt(Body):
    asset_id:UUID4
    profile:Literal['youtube','instagram','facebook','whatsapp','x','tiktok','gmail']
class NewCampaign(Body):
    idempotency_key:UUID4
    asset_id:UUID4
    title:str=Field(min_length=1,max_length=100,pattern=r'^[^\r\n]+$')
    description:str=Field(default='',max_length=2000)
    scheduled_at:datetime
    timezone:str=Field(max_length=80)
    providers:list[Literal['youtube','instagram','facebook','whatsapp','x','tiktok','gmail']]=Field(min_length=1,max_length=7)
    contact_ids:list[UUID4]=Field(default_factory=list,max_length=200)
    options:dict[str,dict]=Field(default_factory=dict)
class Approval(Body):confirm_dispatch:Literal[True]
class Reschedule(Body):scheduled_at:datetime;timezone:str
class MediaOrigin(Body):origin:str=Field(max_length=300)

def contact_dict(row):return {'id':row.id,'provider':row.provider,'address':row.address,'name':row.name,'subscribed':row.subscribed,'consent_source':row.consent_source}
def audience_permission(access):
    access.require_asset_access() if access.permissions.get('publish') else access.require('crm')
def validate_schedule(value,zone):
    if value.tzinfo is None:raise HTTPException(422,'La fecha debe incluir zona horaria u offset UTC.')
    try:ZoneInfo(zone)
    except (ZoneInfoNotFoundError,ValueError):raise HTTPException(422,'Zona horaria no válida.') from None
    if value<cs.now()-timedelta(minutes=5) or value>cs.now()+timedelta(days=365):raise HTTPException(422,'Selecciona una fecha entre ahora y los próximos 365 días.')
    return value.astimezone(cs.UTC)

def options_for(provider,body):
    option=body.options.get(provider,{})
    if provider=='youtube':
        if type(option.get('made_for_kids')) is not bool:raise HTTPException(422,'Clasifica el video de YouTube como creado para niños o no; los envíos son privados.')
        return {'made_for_kids':option['made_for_kids']}
    if provider=='whatsapp':
        name=option.get('template_name','');language=option.get('template_language','es');variables=option.get('template_variables',[])
        if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9_]{1,120}',name) or not isinstance(language,str) or not re.fullmatch(r'[a-z]{2,3}(_[A-Z]{2})?',language) or not isinstance(variables,list) or len(variables)>5 or any(not isinstance(item,str) or len(item)>500 for item in variables):raise HTTPException(422,'Configura la plantilla de WhatsApp aprobada con cabecera de video y sus variables.')
        return {'template_name':name,'template_language':language,'template_variables':variables}
    if provider=='tiktok':
        privacy=option.get('privacy','SELF_ONLY')
        if privacy not in ['SELF_ONLY','PUBLIC_TO_EVERYONE','MUTUAL_FOLLOW_FRIENDS','FOLLOWER_OF_CREATOR']:raise HTTPException(422,'Privacidad de TikTok no válida.')
        return {'privacy':privacy,'disable_comment':True,'is_aigc':option.get('is_aigc') is True}
    if provider=='x':
        text=option.get('text',(body.title+'\n'+body.description).strip())
        if not isinstance(text,str) or not 1<=len(text)<=280:raise HTTPException(422,'El texto para X debe tener entre 1 y 280 caracteres.')
        return {'text':text}
    return {}

@router.get('/settings')
def settings(access=Depends(context),db=Depends(deps.get_db)):
    access.require('publish')
    pulse=db.get(CampaignScheduler,'node6-campaigns')
    try:origin=cs.public_origin(db);media_warning=''
    except HTTPException as error:origin='';media_warning=error.detail
    key=('platform_' if access.owner else '')+'social_posts'
    usage=db.query(ConsumoInquilino).filter_by(inquilino_id=access.tenant.id,periodo=cs.now().strftime('%Y-%m'),capacidad=key).first()
    limit=None if access.owner else access.caps.monthly_limits['social_posts']
    return {'providers':cs.PROVIDERS,'delivery_enabled':cs.delivery_enabled(),'public_media_ready':bool(origin),'media_warning':media_warning,'scheduler_last_seen':cs.aware(pulse.last_seen).isoformat() if pulse else None,'scheduler_recent':bool(pulse and cs.aware(pulse.last_seen)>cs.now()-timedelta(minutes=10)),'monthly_sends':{'limit':limit,'used':usage.cantidad_usada if usage else 0},'max_targets':200,'adaptation':'H.264/AAC, ajuste con bandas sin recortar el original; no consume una nueva generación creativa.'}

@router.put('/settings/media-origin')
def media_origin(body:MediaOrigin,access=Depends(context),db=Depends(deps.get_db)):
    if not access.owner:raise HTTPException(403,'Solo el administrador general configura el dominio público del sistema.')
    value=cs.public_origin(value=body.origin.strip())
    row=db.get(CampaignSetting,'public_media_origin')
    if row is None:row=CampaignSetting(id='public_media_origin');db.add(row)
    row.value=value;db.commit();return {'configured':bool(value),'verified':False}

@router.get('/channels')
def channels(access=Depends(context),db=Depends(deps.get_db)):
    access.require('publish')
    rows=db.query(WorkspaceChannel).filter_by(scope=access.scope).all()
    return {'channels':[{'provider':row.provider,'label':row.label,'configured':True,'verified':False} for row in rows if row.provider in cs.PROVIDERS],'manage_channels':access.manages_team}

@router.put('/channels/{provider}')
async def connect(provider:str,request:Request,access=Depends(context),db=Depends(deps.get_db)):
    access.require('publish')
    if not access.manages_team:raise HTTPException(403,'Solo el administrador conecta las cuentas de su organización.')
    if provider not in cs.PROVIDERS:raise HTTPException(404,'Proveedor no disponible.')
    try:
        body=Connection.model_validate(await request.json());credentials={name:value.get_secret_value().strip() for name,value in body.credentials.items()}
        required=set(cs.PROVIDERS[provider]['fields']);allowed=required|({'api_version'} if provider in ['instagram','facebook','whatsapp'] else set())
        if set(credentials)-allowed or not required.issubset(credentials) or any(not value or len(value)>8192 or '\n' in value or '\r' in value for value in credentials.values()):raise ValueError()
        for key in ['account_id','page_id','phone_number_id']:
            if key in credentials and not re.fullmatch(r'\d{1,40}',credentials[key]):raise ValueError()
        if 'api_version' in credentials and not re.fullmatch(r'v\d{1,2}\.\d',credentials['api_version']):raise ValueError()
        if provider=='gmail':credentials['sender_email']=str(TypeAdapter(EmailStr).validate_python(credentials['sender_email']))
    except (ValueError,ValidationError):raise HTTPException(422,'Completa los campos de la integración; las credenciales no se devolvieron.') from None
    row=cs.channel(db,access,provider)
    if not row:row=WorkspaceChannel(scope=access.scope,provider=provider);db.add(row)
    row.label=body.label;row.encrypted_credentials=ws.encryption().encrypt(json.dumps(credentials).encode()).decode();row.connected_by=access.user.id;db.commit()
    return {'configured':True,'verified':False,'provider':provider}

@router.delete('/channels/{provider}')
def disconnect(provider:str,access=Depends(context),db=Depends(deps.get_db)):
    if not access.manages_team:raise HTTPException(403,'Solo el administrador desconecta las cuentas.')
    db.query(WorkspaceChannel).filter_by(scope=access.scope,provider=provider).delete();db.commit();return {'configured':False}

@router.get('/contacts')
def contacts(access=Depends(context),db=Depends(deps.get_db)):
    audience_permission(access)
    return {'contacts':[contact_dict(row) for row in db.query(CampaignContact).filter_by(scope=access.scope).order_by(CampaignContact.created_at.desc()).limit(1000).all()]}

@router.post('/contacts',status_code=201)
def add_contacts(body:Audience,access=Depends(context),db=Depends(deps.get_db)):
    access.require('crm');normalized=[]
    for item in body.contacts:
        address=item.address.strip()
        try:
            if item.provider=='gmail':address=str(TypeAdapter(EmailStr).validate_python(address)).lower()
            elif not re.fullmatch(r'\+[1-9]\d{7,14}',address):raise ValueError()
        except ValueError:raise HTTPException(422,'Hay un correo o número internacional no válido; no se guardó la importación.') from None
        normalized.append((item,address))
    ids=[]
    for item,address in normalized:
        row=db.query(CampaignContact).filter_by(scope=access.scope,provider=item.provider,address=address).first()
        if row and not row.subscribed:raise HTTPException(409,'Un contacto se dio de baja. No se reactivó desde una importación.')
        if not row:
            row=CampaignContact(id=str(uuid.uuid4()),scope=access.scope,provider=item.provider,address=address,name=item.name,consent_source=item.consent_source,subscribed=True,created_by=access.user.id);db.add(row);db.flush()
        ids.append(row.id)
    db.commit();return {'saved':len(set(ids)),'ids':list(dict.fromkeys(ids))}

@router.put('/contacts/{contact_id}')
def update_contact(contact_id:str,body:Subscription,access=Depends(context),db=Depends(deps.get_db)):
    access.require('crm');row=db.query(CampaignContact).filter_by(id=contact_id,scope=access.scope).first()
    if not row:raise HTTPException(404,'Contacto no encontrado.')
    if body.subscribed and not row.subscribed:raise HTTPException(409,'Una baja requiere renovar el consentimiento; no se reactiva automáticamente.')
    row.subscribed=body.subscribed;db.commit();return {'saved':True}

@router.post('/adaptations')
def adaptation(body:Adapt,access=Depends(context),db=Depends(deps.get_db)):
    access.require('media');asset=ws.asset_for(db,access,str(body.asset_id),'reel')
    return {**ws.asset_dict(cs.adapt_asset(db,access,asset,body.profile)),'profile':body.profile,'source_preserved':True}

@router.get('')
def campaigns(from_at:datetime|None=None,until_at:datetime|None=None,access=Depends(context),db=Depends(deps.get_db)):
    access.require('publish');query=db.query(Campaign).filter_by(scope=access.scope)
    if from_at:
        if from_at.tzinfo is None:raise HTTPException(422,'La fecha inicial requiere zona horaria.')
        query=query.filter(Campaign.scheduled_at>=from_at)
    if until_at:
        if until_at.tzinfo is None:raise HTTPException(422,'La fecha final requiere zona horaria.')
        query=query.filter(Campaign.scheduled_at<until_at)
    return {'campaigns':[cs.campaign_dict(db,row) for row in query.order_by(Campaign.scheduled_at.desc()).limit(200).all()]}

@router.post('',status_code=201)
def create(body:NewCampaign,access=Depends(context),db=Depends(deps.get_db)):
    access.require('publish');asset=ws.asset_for(db,access,str(body.asset_id),'reel')
    digest=hashlib.sha256(json.dumps(body.model_dump(mode='json'),sort_keys=True).encode()).hexdigest()
    existing=db.query(Campaign).filter_by(scope=access.scope,idempotency_key=str(body.idempotency_key)).first()
    if existing:
        if existing.request_hash!=digest:raise HTTPException(409,'La clave de esta campaña ya corresponde a otro contenido. Guarda un borrador nuevo.')
        return cs.campaign_dict(db,existing)
    scheduled=validate_schedule(body.scheduled_at,body.timezone);providers=list(dict.fromkeys(body.providers));targets=[]
    contacts=[]
    for contact_id in set(body.contact_ids):
        contact=db.query(CampaignContact).filter_by(id=str(contact_id),scope=access.scope,subscribed=True).first()
        if not contact:raise HTTPException(404,'Un destinatario no pertenece a tu audiencia activa.')
        if contact.provider not in providers:raise HTTPException(422,'Hay destinatarios cuyo canal no fue seleccionado.')
        contacts.append(contact)
    for provider in providers:
        option=options_for(provider,body)
        if provider in ['gmail','whatsapp']:
            audience=[contact for contact in contacts if contact.provider==provider]
            if not audience:raise HTTPException(422,'Selecciona destinatarios con consentimiento para '+provider+'.')
            targets.extend((provider,contact.id,option) for contact in audience)
        else:targets.append((provider,None,option))
    if len(targets)>200:raise HTTPException(422,'Máximo 200 destinos por campaña.')
    row=Campaign(id=str(uuid.uuid4()),scope=access.scope,idempotency_key=str(body.idempotency_key),request_hash=digest,asset_id=asset.id,title=body.title,description=body.description,scheduled_at=scheduled,timezone=body.timezone,created_by=access.user.id,state='draft');db.add(row);db.flush()
    for provider,contact_id,option in targets:db.add(CampaignTarget(id=str(uuid.uuid4()),campaign_id=row.id,provider=provider,contact_id=contact_id,contact_key=contact_id or 'account',next_at=scheduled,state='draft',options=json.dumps(option)))
    from sqlalchemy.exc import IntegrityError
    try:db.commit()
    except IntegrityError:
        db.rollback();existing=db.query(Campaign).filter_by(scope=access.scope,idempotency_key=str(body.idempotency_key)).first()
        if not existing or existing.request_hash!=digest:raise HTTPException(409,'El borrador cambió durante la solicitud; revisa las campañas guardadas.') from None
        return cs.campaign_dict(db,existing)
    return cs.campaign_dict(db,row)

@router.post('/{campaign_id}/approve')
def approve(campaign_id:str,body:Approval,access=Depends(context),db=Depends(deps.get_db)):
    access.require('publish')
    if not cs.delivery_enabled():raise HTTPException(409,'El servidor está en modo preparación sin envíos. Completa la autorización de cuentas antes de activar el despacho.')
    row=cs.campaign_for(db,access,campaign_id)
    if row.state!='draft':raise HTTPException(409,'Esta campaña ya salió del estado borrador.')
    validate_schedule(cs.aware(row.scheduled_at),row.timezone);cs.authorize_campaign(db,row)
    jobs=db.query(CampaignTarget).filter_by(campaign_id=row.id).all()
    for job in jobs:
        configured=cs.channel(db,access,job.provider)
        if not configured:raise HTTPException(409,'Configura el canal de '+job.provider+' antes de aprobar.')
        if job.provider=='instagram' and not cs.public_origin(db):raise HTTPException(409,'Instagram necesita un dominio público HTTPS para obtener el video.')
        if job.contact_id:
            contact=db.get(CampaignContact,job.contact_id)
            if not contact.subscribed:raise HTTPException(409,'Un destinatario se dio de baja; vuelve a crear la selección de audiencia.')
    limit=None if access.owner else access.caps.monthly_limits['social_posts']
    if limit is not None and len(jobs)>limit:raise HTTPException(429,'La campaña supera la cuota mensual de envíos de tu plan. Reduce la audiencia o amplía tu cupo.')
    # Lock/conditional update prevents double approvals with stale sessions.
    from sqlalchemy import update
    claimed=db.execute(update(Campaign).where(Campaign.id==row.id,Campaign.state=='draft',Campaign.scheduled_at==row.scheduled_at).values(state='scheduled',approved_by=access.user.id).returning(Campaign.id)).scalar_one_or_none()
    if not claimed:raise HTTPException(409,'La campaña ya fue aprobada por otro miembro.')
    for job in jobs:job.channel_fingerprint=cs.fingerprint(cs.channel(db,access,job.provider));job.state='queued'
    db.commit();return cs.campaign_dict(db,row)

@router.post('/{campaign_id}/cancel')
def cancel(campaign_id:str,access=Depends(context),db=Depends(deps.get_db)):
    access.require('publish');row=cs.campaign_for(db,access,campaign_id);row.state='canceled'
    for job in db.query(CampaignTarget).filter(CampaignTarget.campaign_id==row.id,CampaignTarget.state.in_(['draft','queued','blocked','waiting_remote'])).all():
        job.state='unknown' if job.quota_charged else 'canceled'
        if job.quota_charged:job.detail='Seguimiento cancelado; el envío ya se inició. Comprueba el resultado en la plataforma.'
    db.commit()
    return {'canceled_pending':True,'message':'Se detuvieron los pendientes. Un envío ya iniciado no se puede retirar desde el calendario.'}

@router.put('/{campaign_id}/schedule')
def reschedule(campaign_id:str,body:Reschedule,access=Depends(context),db=Depends(deps.get_db)):
    access.require('publish');row=cs.campaign_for(db,access,campaign_id);jobs=db.query(CampaignTarget).filter_by(campaign_id=row.id).all()
    if any(job.quota_charged or job.state not in ['draft','queued','blocked','canceled'] for job in jobs):raise HTTPException(409,'Ya hay envíos iniciados. Conserva su historial y crea otra campaña para los nuevos destinos.')
    scheduled=validate_schedule(body.scheduled_at,body.timezone)
    from sqlalchemy import update
    changed=db.execute(update(CampaignTarget).where(CampaignTarget.campaign_id==row.id,CampaignTarget.state.in_(['draft','queued','blocked','canceled']),CampaignTarget.quota_charged.is_(False)).values(state='draft',next_at=scheduled).returning(CampaignTarget.id)).all()
    if len(changed)!=len(jobs):db.rollback();raise HTTPException(409,'Un envío se inició durante la edición; no se cambió la programación.')
    row.scheduled_at=scheduled;row.timezone=body.timezone;row.state='draft';row.approved_by=None
    for job in jobs:job.state='draft';job.next_at=row.scheduled_at;job.detail='';job.channel_fingerprint=None
    db.commit();return cs.campaign_dict(db,row)

@router.api_route('/media/{target_id}',methods=['GET','HEAD'])
def public_media(target_id:str,request:Request,db=Depends(deps.get_db)):
    token=request.query_params.get('token','');request.scope['query_string']=b'';claims=cs.verify_link(token,'campaign-media')
    job=db.get(CampaignTarget,target_id)
    if not job or claims.get('sub')!=job.id:raise HTTPException(404,'Medio no disponible.')
    campaign=db.get(Campaign,job.campaign_id)
    if claims.get('scope')!=campaign.scope or job.provider!='instagram' or job.state not in ['processing','waiting_remote','published'] or campaign.state=='canceled':raise HTTPException(404,'Medio no disponible.')
    access=cs.authorize_campaign(db,campaign);asset=ws.asset_for(db,access,job.variant_id,'reel');data=ws.worker('/artifacts/'+asset.filename).content
    if len(data)>40*1024*1024:raise HTTPException(413,'Medio demasiado grande.')
    headers={'Cache-Control':'no-store','Accept-Ranges':'bytes','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'}
    if request.method=='HEAD':return Response(b'',media_type='video/mp4',headers={**headers,'Content-Length':str(len(data))})
    value=request.headers.get('range')
    if value:
        match=re.fullmatch(r'bytes=(\d+)-(\d*)',value)
        if not match:raise HTTPException(416,'Rango no disponible.')
        start=int(match[1]);end=min(int(match[2]) if match[2] else len(data)-1,len(data)-1)
        if start>end or start>=len(data):raise HTTPException(416,'Rango no disponible.')
        headers['Content-Range']=f'bytes {start}-{end}/{len(data)}'
        return Response(data[start:end+1],status_code=206,media_type='video/mp4',headers=headers)
    return Response(data,media_type='video/mp4',headers=headers)

@router.api_route('/unsubscribe',methods=['GET','POST'])
async def unsubscribe(request:Request,db=Depends(deps.get_db)):
    token=request.query_params.get('token','');request.scope['query_string']=b'';claims=cs.verify_link(token,'campaign-unsubscribe')
    row=db.query(CampaignContact).filter_by(id=claims.get('sub'),scope=claims.get('scope')).first()
    if not row:raise HTTPException(404,'Enlace no disponible.')
    if request.method=='POST':
        row.subscribed=False;db.commit();return HTMLResponse('<!doctype html><html lang="es"><meta name="viewport" content="width=device-width"><title>Baja registrada</title><body style="background:#070b14;color:#7dd3fc;font:18px sans-serif;padding:2rem"><h1 style="color:#38bdf8">Baja registrada</h1><p>No recibirás nuevos envíos de esta audiencia.</p></body></html>',headers={'Cache-Control':'no-store'})
    # GET does not unsubscribe: automated email scanners must not remove consent.
    from html import escape
    return HTMLResponse('<!doctype html><html lang="es"><meta name="viewport" content="width=device-width"><title>Preferencias SGA-CD</title><body style="background:#070b14;color:#7dd3fc;font:18px sans-serif;padding:2rem"><h1>Preferencias de comunicación</h1><form method="post" action="?token='+escape(token,quote=True)+'"><button style="background:#38bdf8;border:0;border-radius:12px;padding:1rem">Dejar de recibir estos mensajes</button></form></body></html>',headers={'Cache-Control':'no-store','Referrer-Policy':'no-referrer','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'"})
