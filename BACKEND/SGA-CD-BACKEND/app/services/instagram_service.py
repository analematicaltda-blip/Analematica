"""Instagram unified login: isolated system-user grants, no automatic publishing."""
import hmac
import json
import re
import secrets
from datetime import timedelta
from urllib.parse import urlencode
from fastapi import HTTPException
from sqlalchemy import update
from app.models.advertising import MetaAdsApp, InstagramLoginConfig, InstagramAuthorization, InstagramOAuthState
from app.models.user import Usuario
from app.services import meta_ads_service as meta
from app.services.meta_ads_graph import MetaGraph, MetaGraphError

CALLBACK = '/api/v1/workspace/instagram/oauth/callback'
REQUIRED = {'instagram_basic', 'instagram_content_publish', 'instagram_manage_comments', 'instagram_manage_messages'}

def configure(db, actor, config_id):
    if not actor.owner: raise HTTPException(403, 'Solo el dueño configura el inicio de sesión de Instagram.')
    row=db.get(InstagramLoginConfig,1)
    if row: row.config_id=config_id;row.revision+=1
    else: db.add(InstagramLoginConfig(id=1,config_id=config_id,revision=1))
    db.commit()
    return {'saved':True,'config_id':config_id}

def status(db, actor):
    config=db.get(InstagramLoginConfig,1);app=db.get(MetaAdsApp,1);auth=db.get(InstagramAuthorization,actor.scope)
    valid=bool(app and auth and auth.app_id==app.app_id and (auth.expires_at is None or meta.aware(auth.expires_at)>meta.now()))
    return {'config_id':config.config_id if config else '', 'app_configured':bool(app), 'authorized_on_record':valid,
            'account':json.loads(auth.account) if valid else {}, 'permissions':json.loads(auth.permissions) if valid else [],
            'publishing_enabled':False,'messaging_enabled':False,'webhooks_configured':False}

def start(db,actor,redirect_uri):
    meta.manager(actor)
    app=db.get(MetaAdsApp,1);config=db.get(InstagramLoginConfig,1)
    # Shared registry stores exact callbacks, validated separately by each flow.
    if not app or not config:raise HTTPException(409,'Configura primero la aplicación y el ajuste de Instagram.')
    if redirect_uri not in json.loads(app.redirect_uris):raise HTTPException(422,'Registra el retorno exacto de Instagram en la aplicación.')
    if not redirect_uri.endswith(CALLBACK):raise HTTPException(422,'Retorno de Instagram no válido.')
    state=secrets.token_urlsafe(32);browser=secrets.token_urlsafe(32)
    db.add(InstagramOAuthState(state_hash=meta.digest(state),browser_hash=meta.digest(browser),scope=actor.scope,actor_id=actor.user.id,app_revision=app.revision,config_revision=config.revision,redirect_uri=redirect_uri,expires_at=meta.now()+timedelta(minutes=10)))
    db.commit()
    params={'client_id':app.app_id,'config_id':config.config_id,'redirect_uri':redirect_uri,'response_type':'code','state':state}
    return {'authorization_url':'https://www.facebook.com/'+app.api_version+'/dialog/oauth?'+urlencode(params),'browser':browser,'state':state,'secure':redirect_uri.startswith('https://')}

def finish(db,state,browser,code,denied=False):
    row=db.get(InstagramOAuthState,meta.digest(state or ''))
    if not row or not browser or not hmac.compare_digest(row.browser_hash,meta.digest(browser)) or row.used_at or meta.aware(row.expires_at)<=meta.now():raise HTTPException(400,'Autorización vencida o ajena a este navegador.')
    app=db.get(MetaAdsApp,1);config=db.get(InstagramLoginConfig,1);user=db.get(Usuario,row.actor_id)
    if not app or not config or app.revision!=row.app_revision or config.revision!=row.config_revision or not user or not user.activo:raise HTTPException(400,'Cambió la configuración o el acceso.')
    actor=meta.actor_for(db,user);meta.manager(actor)
    if actor.scope!=row.scope:raise HTTPException(400,'La organización cambió.')
    count=db.execute(update(InstagramOAuthState).where(InstagramOAuthState.state_hash==row.state_hash,InstagramOAuthState.used_at.is_(None)).values(used_at=meta.now())).rowcount
    db.commit()
    if count!=1:raise HTTPException(400,'Autorización ya utilizada.')
    if denied or not code:return False
    try:
        secret=meta.decrypted(app.encrypted_secret)
        result=MetaGraph(app.api_version,app.app_id,secret).exchange_system(code,row.redirect_uri)
        # Introspect with app credentials; never trust token response flags alone.
        debug=MetaGraph(app.api_version,app.app_id,secret,app.app_id+'|'+secret).get('debug_token',input_token=result['access_token']).get('data',{})
        scopes=debug.get('scopes',[])
        if not isinstance(scopes,list) or not all(isinstance(p,str) for p in scopes) or debug.get('is_valid') is not True or str(debug.get('app_id'))!=app.app_id or not REQUIRED.issubset(set(scopes)):raise MetaGraphError('permission_missing',403)
        expiry=debug.get('expires_at')
        if not isinstance(expiry,int) or isinstance(expiry,bool) or expiry<0:raise MetaGraphError('response_invalid')
        expires=meta.now().fromtimestamp(expiry,meta.UTC) if expiry else None
        if expires and expires<=meta.now():raise MetaGraphError('authorization_expired',401)
        auth=db.get(InstagramAuthorization,actor.scope)
        if not auth:auth=InstagramAuthorization(scope=actor.scope,app_id=app.app_id,encrypted_token='',connected_by=actor.user.id);db.add(auth)
        auth.app_id=app.app_id;auth.encrypted_token=meta.encrypted(result['access_token']);auth.permissions=json.dumps(scopes);auth.expires_at=expires;auth.account='{}';auth.connected_by=actor.user.id
        db.commit();return True
    except (MetaGraphError,HTTPException,ValueError,OverflowError):
        db.rollback();return False

def select_account(db,actor,account_id):
    meta.manager(actor);app=db.get(MetaAdsApp,1);auth=db.get(InstagramAuthorization,actor.scope)
    if not app or not auth or auth.app_id!=app.app_id or (auth.expires_at and meta.aware(auth.expires_at)<=meta.now()):raise HTTPException(409,'Autoriza primero Instagram.')
    try:
        body=MetaGraph(app.api_version,app.app_id,meta.decrypted(app.encrypted_secret),meta.decrypted(auth.encrypted_token)).get(account_id,fields='id,username')
    except MetaGraphError:raise HTTPException(502,'No se pudo comprobar esa cuenta en Meta.') from None
    if str(body.get('id'))!=account_id or not re.fullmatch(r'[A-Za-z0-9_.]{1,80}',str(body.get('username',''))):raise HTTPException(502,'Meta no devolvió una cuenta válida.')
    auth.account=json.dumps({'id':account_id,'username':body['username']});db.commit()
    return {'account':json.loads(auth.account)}
