"""Server-side campaign policy, encrypted channels, adaptation and dispatch orchestration."""
from datetime import datetime,timedelta,timezone
import hashlib
import json
import os
import uuid
from urllib.parse import urlparse,urlencode
from jose import jwt,JWTError
from fastapi import HTTPException
from sqlalchemy import update
from app.core.config import settings
from app.models.user import Usuario
from app.models.workspace import WorkspaceAsset,WorkspaceChannel
from app.models.campaigns import Campaign,CampaignTarget,CampaignContact,CampaignVariant,CampaignSetting
from app.services import workspace_service as ws

UTC=timezone.utc
PROVIDERS={
 'youtube':{'label':'YouTube · privado','fields':['client_id','client_secret','refresh_token']},
 'instagram':{'label':'Instagram Reels · Meta','fields':['account_id','access_token']},
 'facebook':{'label':'Facebook Video · Meta','fields':['page_id','access_token']},
 'whatsapp':{'label':'WhatsApp Business · Meta','fields':['phone_number_id','access_token']},
 'x':{'label':'X','fields':['consumer_key','consumer_secret','access_token','access_secret']},
 'tiktok':{'label':'TikTok','fields':['access_token']},
 'gmail':{'label':'Gmail','fields':['sender_email','client_id','client_secret','refresh_token']},
}
FINAL={'published','accepted','rejected','blocked','unknown','canceled'}

def delivery_enabled():return os.getenv('CAMPAIGN_DELIVERY_ENABLED','0')=='1'
def now():return datetime.now(UTC)
def aware(value):return value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
def channel(db,access,provider):return db.query(WorkspaceChannel).filter_by(scope=access.scope,provider=provider).first()
def fingerprint(row):return hashlib.sha256(row.encrypted_credentials.encode()).hexdigest()
def campaign_for(db,access,campaign_id):
    row=db.query(Campaign).filter_by(id=campaign_id,scope=access.scope).first()
    if not row:raise HTTPException(404,'Campaña no encontrada en tu organización.')
    return row

def public_origin(db=None,value=None):
    stored=db.get(CampaignSetting,'public_media_origin') if db is not None and value is None else None
    value=(stored.value if stored else os.getenv('PUBLISH_MEDIA_ORIGIN','')) if value is None else value
    value=value.rstrip('/')
    if not value:return ''
    try:parsed=urlparse(value);port=parsed.port
    except ValueError:raise HTTPException(503,'El origen de medios no es una URL HTTPS válida.') from None
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or port not in [None,443] or parsed.path or parsed.query or parsed.fragment or parsed.hostname.endswith('.app.github.dev') or parsed.hostname in ['localhost','127.0.0.1']:
        raise HTTPException(503,'Configura un dominio HTTPS público para medios; los puertos privados de Codespaces no son accesibles por Instagram.')
    return value

def link_token(kind,subject,scope,expires):
    return jwt.encode({'type':kind,'sub':subject,'scope':scope,'exp':now()+expires},settings.SECRET_KEY,algorithm=settings.ALGORITHM)
def verify_link(token,kind):
    try:
        value=jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        if value.get('type')!=kind:raise JWTError()
        return value
    except JWTError:raise HTTPException(404,'Enlace no disponible o vencido.') from None

def adapt_asset(db,access,asset,provider):
    cached=db.query(CampaignVariant).filter_by(source_id=asset.id,profile=provider).first()
    if cached:return ws.asset_for(db,access,cached.asset_id,'reel')
    try:
        result=ws.worker('/internal/campaigns/adapt',{'filename':asset.filename,'profile':provider}).json()
        info=ws.save_asset(db,access,result,'reel',asset.title+' · '+provider,commit=False)
        row=CampaignVariant(source_id=asset.id,profile=provider,asset_id=info['id']);db.add(row);db.commit()
        return ws.asset_for(db,access,info['id'],'reel')
    except Exception:
        db.rollback();raise

def authorize_campaign(db,campaign):
    user=db.get(Usuario,campaign.created_by)
    if not user:raise HTTPException(403,'El autor de la campaña ya no está disponible.')
    access=ws.access_for(db,user);access.require('publish')
    if access.scope!=campaign.scope:raise HTTPException(403,'La campaña ya no pertenece al espacio del autor.')
    if campaign.approved_by and campaign.approved_by!=campaign.created_by:
        approver=db.get(Usuario,campaign.approved_by)
        if not approver:raise HTTPException(403,'La aprobación ya no es válida.')
        approval=ws.access_for(db,approver);approval.require('publish')
        if approval.scope!=campaign.scope:raise HTTPException(403,'La aprobación ya no pertenece a esta organización.')
    return access

def campaign_dict(db,row):
    pairs=db.query(CampaignTarget,CampaignContact).outerjoin(CampaignContact,CampaignTarget.contact_id==CampaignContact.id).filter(CampaignTarget.campaign_id==row.id).all()
    jobs=[job for job,contact in pairs]
    recipients={job.id:contact.address for job,contact in pairs if contact and contact.scope==row.scope}
    counts={}
    for job in jobs:counts[job.state]=counts.get(job.state,0)+1
    state=row.state
    if state not in ['draft','canceled']:
        state='scheduled' if jobs and all(job.state=='queued' and job.claimed_at is None for job in jobs) else 'processing' if any(job.state not in FINAL for job in jobs) else 'completed' if all(job.state in ['published','accepted'] for job in jobs) else 'needs_review'
    return {'id':row.id,'asset_id':row.asset_id,'title':row.title,'description':row.description,'state':state,'scheduled_at':aware(row.scheduled_at).isoformat(),'timezone':row.timezone,'counts':counts,'can_reschedule':all(not job.quota_charged and job.state in ['draft','queued','blocked','canceled'] for job in jobs),'targets':[{'id':job.id,'provider':job.provider,'state':job.state,'next_at':aware(job.next_at).isoformat(),'remote_id':job.remote_id,'detail':job.detail,'contact_id':job.contact_id,'recipient':recipients.get(job.id)} for job in jobs]}

def apply_result(db,job,result,advance=True):
    outcome=result.get('outcome')
    if outcome not in ['pending','published','accepted','rejected','unknown']:outcome='unknown'
    job.provider_state=json.dumps(result.get('provider_state',{}))
    job.remote_id=str(result.get('remote_id') or job.remote_id or '')[:200] or None
    job.detail=str(result.get('detail',''))[:250]
    if advance:job.phase+=1
    if outcome=='pending':job.state='waiting_remote';job.next_at=now()+timedelta(seconds=30)
    elif outcome=='rejected' and isinstance(result.get('retry_after'),int) and result['retry_after']>0:
        job.state='queued';job.next_at=now()+timedelta(seconds=min(3600,max(30,result['retry_after'])));job.detail='Límite de frecuencia de la plataforma; espera programada.'
    else:
        job.state=outcome
        if outcome=='unknown':job.next_at=now()+timedelta(minutes=5)
    db.commit()

def dispatch_job(db,job_id):
    if not delivery_enabled():return
    job=db.get(CampaignTarget,job_id);campaign=db.get(Campaign,job.campaign_id)
    try:
        if campaign.state=='canceled':
            job.state='unknown' if job.quota_charged else 'canceled'
            if job.quota_charged:job.detail='Seguimiento cancelado; comprueba en la plataforma el envío ya iniciado.'
            db.commit();return
        if aware(campaign.scheduled_at)<now()-timedelta(hours=24):raise HTTPException(409,'La programación tiene más de 24 horas de retraso. Revisa el calendario antes de enviar.')
        access=authorize_campaign(db,campaign)
        configured=channel(db,access,job.provider)
        if not configured or fingerprint(configured)!=job.channel_fingerprint:raise HTTPException(409,'El canal cambió o fue desconectado. Revisa y aprueba de nuevo los pendientes.')
        credentials=ws.channel_credentials(db,access,job.provider)
        recipient=''
        if job.contact_id:
            contact=db.get(CampaignContact,job.contact_id)
            if not contact or contact.scope!=access.scope or not contact.subscribed or contact.provider!=job.provider:raise HTTPException(409,'El destinatario se dio de baja o ya no pertenece a esta audiencia.')
            from app.commercial.pool08.crm_delivery_guard import require_not_suppressed
            require_not_suppressed(db,access.scope,job.provider,contact.address)
            recipient=contact.address
        if job.variant_id:asset=ws.asset_for(db,access,job.variant_id,'reel')
        else:
            source=ws.asset_for(db,access,campaign.asset_id,'reel');asset=adapt_asset(db,access,source,job.provider);job.variant_id=asset.id;db.commit()
        # Adaptation may take time: re-check permission, channel and cancellation before sending.
        db.expire_all();job=db.get(CampaignTarget,job_id);campaign=db.get(Campaign,job.campaign_id)
        if campaign.state=='canceled':
            job.state='unknown' if job.quota_charged else 'canceled'
            if job.quota_charged:job.detail='Seguimiento cancelado; comprueba en la plataforma el envío ya iniciado.'
            db.commit();return
        access=authorize_campaign(db,campaign);configured=channel(db,access,job.provider)
        if not configured or fingerprint(configured)!=job.channel_fingerprint:raise HTTPException(409,'El canal cambió durante la preparación.')
        if job.contact_id:
            contact=db.get(CampaignContact,job.contact_id)
            if not contact.subscribed:raise HTTPException(409,'El destinatario se dio de baja durante la preparación.')
            from app.commercial.pool08.crm_delivery_guard import require_not_suppressed
            require_not_suppressed(db,access.scope,job.provider,contact.address)
        origin=public_origin(db) if job.provider in ['instagram','gmail'] else ''
        if job.provider=='instagram' and not origin:raise HTTPException(409,'Instagram necesita un dominio público HTTPS para obtener el video.')
        if not job.quota_charged:
            ws.reserve(db,access,'social_posts');job.quota_charged=True;db.commit()
        media=origin+'/api/v1/workspace/campaigns/media/'+job.id+'?'+urlencode({'token':link_token('campaign-media',job.id,access.scope,timedelta(hours=12))}) if origin and job.provider=='instagram' else ''
        unsubscribe=origin+'/api/v1/workspace/campaigns/unsubscribe?'+urlencode({'token':link_token('campaign-unsubscribe',job.contact_id,access.scope,timedelta(days=180))}) if origin and job.provider=='gmail' else ''
        payload={'workspace':access.scope,'job_id':job.id,'phase':job.phase,'provider':job.provider,'filename':asset.filename,'credentials':credentials,'title':campaign.title,'description':campaign.description,'recipient':recipient,'provider_state':json.loads(job.provider_state),'options':json.loads(job.options),'public_video_url':media,'unsubscribe_url':unsubscribe}
    except HTTPException as error:
        db.rollback();job=db.get(CampaignTarget,job_id);job.state='blocked';job.detail=str(error.detail)[:250];db.commit();return
    except Exception:
        db.rollback();job=db.get(CampaignTarget,job_id);job.state='blocked';job.detail='No se pudo preparar el video o comprobar la configuración; no se inició un envío nuevo.';db.commit();return
    try:result=ws.worker('/internal/campaigns/deliver',payload).json()
    except Exception:
        # The external side effect could already have happened. Never enqueue blindly.
        result={'outcome':'unknown','detail':'Conexión interrumpida; comprueba la plataforma antes de repetir.'}
    apply_result(db,job,result)

def tick(db,limit=10):
    if not delivery_enabled():return 0
    instant=now()
    # Recover only by reading Node 6's journal; do not resend uncertain in-flight jobs.
    abandoned=db.query(CampaignTarget).filter(CampaignTarget.state=='processing',CampaignTarget.claimed_at<instant-timedelta(minutes=15)).limit(limit).all()
    for job in abandoned:
        campaign=db.get(Campaign,job.campaign_id)
        try:
            cached=ws.worker(f'/internal/campaigns/result/{campaign.scope}/{job.id}/{job.phase}').json()
            value=cached.get('result') if cached.get('status')=='complete' else None
        except Exception:value=None
        apply_result(db,job,value or {'outcome':'unknown','detail':'Proceso interrumpido; resultado pendiente de comprobación manual.'})
    # Read-only reconciliation can confirm a late response without repeating its POST.
    uncertain=db.query(CampaignTarget).filter(CampaignTarget.state=='unknown',CampaignTarget.phase>0,CampaignTarget.claimed_at<instant-timedelta(minutes=5),CampaignTarget.claimed_at>instant-timedelta(days=7),CampaignTarget.next_at<=instant).limit(limit).all()
    for job in uncertain:
        campaign=db.get(Campaign,job.campaign_id)
        try:
            cached=ws.worker(f'/internal/campaigns/result/{campaign.scope}/{job.id}/{job.phase-1}').json()
            value=cached.get('result') if cached.get('status')=='complete' else None
        except Exception:value=None
        if value and value.get('outcome') in ['published','accepted','rejected','pending'] and not (campaign.state=='canceled' and value.get('outcome')=='pending'):
            apply_result(db,job,value,advance=False)
        else:job.next_at=instant+timedelta(minutes=15);db.commit()
    candidates=db.query(CampaignTarget.id,CampaignTarget.state).filter(CampaignTarget.state.in_(['queued','waiting_remote']),CampaignTarget.next_at<=instant).order_by(CampaignTarget.next_at).limit(limit).all()
    processed=0
    for job_id,previous in candidates:
        claim=db.execute(update(CampaignTarget).where(CampaignTarget.id==job_id,CampaignTarget.state==previous,CampaignTarget.next_at<=instant).values(state='processing',claimed_at=instant).returning(CampaignTarget.id)).scalar_one_or_none();db.commit()
        if claim:dispatch_job(db,job_id);processed+=1
    return processed
