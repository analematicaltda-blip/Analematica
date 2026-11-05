"""Meta Ads OAuth/read integration. Shared app, isolated authorizations, local-only drafts."""
import hashlib
import hmac
import json
import re
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode, urlsplit
from fastapi import HTTPException
from sqlalchemy import update
from cryptography.fernet import InvalidToken
from app.models.advertising import MetaAdsApp, MetaAdsAuthorization, MetaAdsOAuthState, AdvertisingProfile
from app.models.user import Usuario
from app.services import workspace_service as ws
from app.services.corporate_policy import require_owner
from app.services.meta_ads_graph import MetaGraph, MetaGraphError

UTC = timezone.utc
CALLBACK = '/api/v1/workspace/ads/meta/oauth/callback'
SCOPES = ['ads_read', 'pages_show_list', 'pages_read_engagement', 'instagram_basic']
GRAPH_VERSION = 'v26.0'  # facebook/facebook-python-business-sdk apiconfig.py, consulted 2026-11-04
MESSAGES = {
    'authorization_expired': 'Meta requiere una nueva autorización.',
    'permission_missing': 'Meta no concedió el permiso necesario para esta consulta.',
    'rate_limited': 'Meta limitó temporalmente las consultas. Reintenta más tarde.',
}

def now(): return datetime.now(UTC)
def aware(value): return value.replace(tzinfo=UTC) if value and value.tzinfo is None else value
def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def encrypted(value): return ws.encryption().encrypt(value.encode()).decode()
def decrypted(value):
    try: return ws.encryption().decrypt(value.encode()).decode()
    except (InvalidToken, ValueError): raise HTTPException(409, 'Reconfigura la conexión; no se pudieron recuperar sus credenciales.') from None

def actor_for(db, user):
    actor = ws.access_for(db, user)
    if actor.owner: return require_owner(db, user)
    actor.require('publish')
    return actor

def manager(actor):
    if not actor.manages_team: raise HTTPException(403, 'Solo el administrador de la organización conecta sus cuentas publicitarias.')

def profiles(db, scope):
    return [{'network':p.network, 'url':p.public_url, 'handle':p.handle, 'declared_id':p.declared_id, 'verified_id':p.verified_id, 'verified_at':p.verified_at.isoformat() if p.verified_at else None, 'state':'verified_on_record' if p.verified_id else 'declared', 'api':'separate_x_authorization_required' if p.network=='x' else 'meta'} for p in db.query(AdvertisingProfile).filter_by(scope=scope).order_by(AdvertisingProfile.id)]

def app_metadata(db):
    app = db.get(MetaAdsApp, 1)
    return {'configured':bool(app), 'app_id':app.app_id if app else '', 'api_version':app.api_version if app else GRAPH_VERSION, 'login_config_id':app.login_config_id if app else '', 'redirect_uris':json.loads(app.redirect_uris) if app else [], 'secret_configured':bool(app and app.encrypted_secret)}

def status(db, actor):
    app = db.get(MetaAdsApp, 1); auth = db.get(MetaAdsAuthorization, actor.scope)
    ready = bool(app and auth and auth.app_id==app.app_id and not auth.invalid_reason and (auth.expires_at is None or aware(auth.expires_at)>now()))
    return {'app':app_metadata(db), 'manage_app':actor.owner, 'manage_connection':actor.manages_team, 'authorized':ready, 'expires_at':auth.expires_at.isoformat() if auth and auth.expires_at else None, 'permissions':json.loads(auth.permissions) if ready else [], 'account':json.loads(auth.account) if ready else {}, 'verified_at':auth.verified_at.isoformat() if auth and auth.verified_at else None, 'profiles':profiles(db,actor.scope), 'mode':'read_only_and_local_drafts', 'live_spend_enabled':False, 'can_write_ads':False, 'organic_publishing':'separate_integration', 'messaging':'separate_webhooks_and_permissions'}

def validate_redirect(uri):
    try:
        p=urlsplit(uri);p.port
    except ValueError:raise HTTPException(422, 'Dirección de retorno no válida.') from None
    local=p.hostname in ['localhost','127.0.0.1']
    if (p.scheme!='https' and not (local and p.scheme=='http')) or not p.hostname or p.username or p.password or p.path not in [CALLBACK, '/api/v1/workspace/instagram/oauth/callback'] or p.query or p.fragment or len(uri)>500:
        raise HTTPException(422, 'Registra una URL HTTPS exacta para el callback de Meta. HTTP solo se admite en localhost.')
    return uri

def configure_app(db, actor, body):
    if not actor.owner: raise HTTPException(403, 'Solo el dueño configura la aplicación compartida de Meta.')
    uris=list(dict.fromkeys(validate_redirect(uri.strip()) for uri in body.redirect_uris))
    app=db.get(MetaAdsApp,1); secret=body.client_secret.get_secret_value().strip() if body.client_secret else ''
    if not secret and (not app or app.app_id!=body.app_id): raise HTTPException(422, 'Ingresa el secreto de esa aplicación en el panel privado.')
    if secret and (len(secret)>8192 or '\n' in secret or '\r' in secret): raise HTTPException(422, 'Secreto de aplicación no válido.')
    if not app:
        app=MetaAdsApp(id=1,app_id=body.app_id,api_version=body.api_version,encrypted_secret=encrypted(secret),redirect_uris=json.dumps(uris),configured_by=actor.user.id,revision=1);db.add(app)
    else:
        app.revision+=1;app.app_id=body.app_id;app.api_version=body.api_version
        if secret:app.encrypted_secret=encrypted(secret)
    app.login_config_id=body.login_config_id;app.redirect_uris=json.dumps(uris);app.configured_by=actor.user.id
    db.commit();return {'saved':True,'app':app_metadata(db)}

def start_oauth(db, actor, redirect_uri, return_path):
    manager(actor);app=db.get(MetaAdsApp,1)
    if not app:raise HTTPException(409,'Primero crea y configura la aplicación de Meta desde Analemática.')
    if redirect_uri not in json.loads(app.redirect_uris):raise HTTPException(422,'Esta dirección de retorno no está registrada en la configuración de la aplicación.')
    allowed=['/admin.html#tab-meta-ads'] if actor.owner else ['/app.html#/admin_empresa/full/canales','/sga/app.html#/admin_empresa/full/canales']
    if return_path not in allowed:raise HTTPException(422,'Destino de retorno no permitido para tu cuenta.')
    state=secrets.token_urlsafe(32);browser=secrets.token_urlsafe(32)
    db.add(MetaAdsOAuthState(state_hash=digest(state),browser_hash=digest(browser),scope=actor.scope,actor_id=actor.user.id,app_revision=app.revision,redirect_uri=redirect_uri,return_path=return_path,expires_at=now()+timedelta(minutes=10)))
    db.commit()
    params={'client_id':app.app_id,'redirect_uri':redirect_uri,'response_type':'code','state':state}
    if app.login_config_id:params['config_id']=app.login_config_id
    else:params['scope']=','.join(SCOPES)
    return {'authorization_url':'https://www.facebook.com/'+app.api_version+'/dialog/oauth?'+urlencode(params),'state':state,'browser':browser,'secure':urlsplit(redirect_uri).scheme=='https'}

def finish_oauth(db, state_value, browser, code, denied=False):
    row=db.get(MetaAdsOAuthState,digest(state_value or ''))
    if not row or not browser or not hmac.compare_digest(row.browser_hash,digest(browser)) or row.used_at or aware(row.expires_at)<=now():
        raise HTTPException(400,'La autorización venció o no pertenece a este navegador. Iníciala de nuevo desde el panel.')
    app=db.get(MetaAdsApp,1);user=db.get(Usuario,row.actor_id)
    if not app or app.revision!=row.app_revision or not user or not user.activo:raise HTTPException(400,'La configuración o el acceso cambió. Inicia de nuevo la autorización.')
    actor=actor_for(db,user);manager(actor)
    if actor.scope!=row.scope:raise HTTPException(403,'La organización de la sesión cambió.')
    claimed=db.execute(update(MetaAdsOAuthState).where(MetaAdsOAuthState.state_hash==row.state_hash,MetaAdsOAuthState.used_at.is_(None)).values(used_at=now(),outcome='processing')).rowcount
    db.commit()
    if claimed!=1:raise HTTPException(400,'Esta autorización ya se utilizó.')
    if denied or not code:row.outcome='denied';db.commit();return row.return_path,False
    try:
        graph=MetaGraph(app.api_version,app.app_id,decrypted(app.encrypted_secret));token=graph.exchange(code,row.redirect_uri)
        probe=MetaGraph(app.api_version,app.app_id,graph.secret,token['access_token'])
        principal=probe.get('me',fields='id');permissions=probe.get('me/permissions').get('data',[])
        if not isinstance(permissions,list):raise MetaGraphError('response_invalid')
        granted=[p['permission'] for p in permissions if isinstance(p,dict) and p.get('status')=='granted' and isinstance(p.get('permission'),str)]
        if not {'ads_read','ads_management'}&set(granted):raise MetaGraphError('permission_missing',403)
        if not re.fullmatch(r'\d{1,40}',str(principal.get('id',''))):raise MetaGraphError('response_invalid')
        expiry=token.get('expires_in');expires=now()+timedelta(seconds=expiry) if isinstance(expiry,int) and 0<expiry<366*86400 else None
        auth=db.get(MetaAdsAuthorization,actor.scope)
        if not auth:auth=MetaAdsAuthorization(scope=actor.scope,app_id=app.app_id,encrypted_token=encrypted(token['access_token']),principal_id=str(principal['id']),connected_by=actor.user.id);db.add(auth)
        else:auth.encrypted_token=encrypted(token['access_token']);auth.app_id=app.app_id;auth.principal_id=str(principal['id'])
        auth.permissions=json.dumps(granted);auth.expires_at=expires;auth.invalid_reason=None;auth.connected_by=actor.user.id;auth.verified_at=now();auth.account='{}'
        row.outcome='authorized';db.commit();return row.return_path,True
    except (MetaGraphError,HTTPException):
        db.rollback();row=db.get(MetaAdsOAuthState,digest(state_value));row.outcome='failed';db.commit();return row.return_path,False

def client(db,actor):
    app=db.get(MetaAdsApp,1);auth=db.get(MetaAdsAuthorization,actor.scope)
    if not app or not auth or auth.app_id!=app.app_id:raise HTTPException(409,'Conecta primero tu autorización de Meta.')
    if auth.invalid_reason or auth.expires_at and aware(auth.expires_at)<=now():raise HTTPException(401,'Autoriza nuevamente tu cuenta en Meta.')
    return auth,MetaGraph(app.api_version,app.app_id,decrypted(app.encrypted_secret),decrypted(auth.encrypted_token))

def call(db,actor,path,**params):
    auth,graph=client(db,actor)
    try:return graph.get(path,**params)
    except MetaGraphError as error:
        if error.kind=='authorization_expired':auth.invalid_reason=error.kind;db.commit()
        raise HTTPException(error.status,MESSAGES.get(error.kind,'No se pudo completar la consulta a Meta. No se cambiaron anuncios.')) from None

def collection(body):
    rows=body.get('data')
    if not isinstance(rows,list):raise HTTPException(502,'Meta devolvió una lista no válida.')
    paging=body.get('paging') if isinstance(body.get('paging'),dict) else {}
    cursors=paging.get('cursors') if isinstance(paging.get('cursors'),dict) else {}
    # Never expose/follow paging.next: it may carry provider credentials.
    cursor=cursors.get('after') if paging.get('next') else None
    return rows,cursor if isinstance(cursor,str) and len(cursor)<=2048 else None

def accounts(db,actor,cursor=None):
    body=call(db,actor,'me/adaccounts',fields='id,name,currency,timezone_name,account_status',limit=100,**({'after':cursor} if cursor else {}));rows,next_cursor=collection(body)
    return {'accounts':[account_data(r) for r in rows if isinstance(r,dict)],'next_cursor':next_cursor}

def account_data(row):
    if not re.fullmatch(r'act_\d{1,40}',str(row.get('id',''))) or not re.fullmatch(r'[A-Z]{3}',str(row.get('currency',''))):raise HTTPException(502,'Meta devolvió datos de cuenta no válidos.')
    return {key:row.get(key) for key in ['id','name','currency','timezone_name','account_status']}

def select_account(db,actor,account_id):
    manager(actor);selected=account_data(call(db,actor,account_id,fields='id,name,currency,timezone_name,account_status'))
    if selected['id']!=account_id:raise HTTPException(502,'Meta no confirmó la cuenta solicitada.')
    auth=db.get(MetaAdsAuthorization,actor.scope);auth.account=json.dumps(selected);db.commit();return {'selected':selected}

def selected(db,actor):
    auth,_=client(db,actor);account=json.loads(auth.account)
    if not account:raise HTTPException(409,'Selecciona explícitamente una cuenta publicitaria autorizada.')
    return account

def campaigns(db,actor,cursor=None):
    account=selected(db,actor);rows,next_cursor=collection(call(db,actor,account['id']+'/campaigns',fields='id,name,status,effective_status,objective',limit=100,**({'after':cursor} if cursor else {})))
    return {'campaigns':[{k:r.get(k) for k in ['id','name','status','effective_status','objective']} for r in rows if isinstance(r,dict)],'next_cursor':next_cursor,'account':account,'queried_at':now().isoformat()}

def insights(db,actor,preset):
    account=selected(db,actor);rows,next_cursor=collection(call(db,actor,account['id']+'/insights',fields='campaign_id,campaign_name,impressions,reach,clicks,ctr,cpc,cpm,spend,actions,cost_per_action_type,date_start,date_stop',level='campaign',date_preset=preset,limit=100))
    allowed=['campaign_id','campaign_name','impressions','reach','clicks','ctr','cpc','cpm','spend','actions','cost_per_action_type','date_start','date_stop']
    return {'insights':[{k:r[k] for k in allowed if k in r} for r in rows if isinstance(r,dict)],'next_cursor':next_cursor,'account':account,'queried_at':now().isoformat(),'attribution_note':'Meta puede actualizar conversiones con retraso. No se deduce CPA a partir de clics.'}

def verify_profiles(db,actor):
    rows,_=collection(call(db,actor,'me/accounts',fields='id,name,instagram_business_account{id,username}',limit=100))
    fb=db.query(AdvertisingProfile).filter_by(scope=actor.scope,network='facebook').first();ig=db.query(AdvertisingProfile).filter_by(scope=actor.scope,network='instagram').first()
    match=next((r for r in rows if isinstance(r,dict) and fb and r.get('id')==fb.declared_id),None)
    if fb:fb.verified_id=str(match['id']) if match else None;fb.verified_at=now() if match else None
    linked=match.get('instagram_business_account',{}) if match else {}
    if ig:
        valid=isinstance(linked,dict) and str(linked.get('username','')).lower()==ig.handle.lower() and re.fullmatch(r'\d{1,40}',str(linked.get('id','')))
        ig.verified_id=str(linked['id']) if valid else None;ig.verified_at=now() if valid else None
    db.commit();return {'profiles':profiles(db,actor.scope),'pages_checked':len(rows),'complete':not bool(_),'note':'Se comprobaron las páginas de esta respuesta; no se eligió la primera página ni se autorizó X.'}
