"""Signature-verified, encrypted inbox. No automated replies or outbound sends."""
import hashlib
import hmac
import json
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, ConfigDict, Field, SecretStr
from sqlalchemy.exc import IntegrityError
from app.api import deps
from app.api.v1.endpoints.instagram import owner
from app.models.advertising import MetaWebhookConfig, MetaWebhookEvent, MetaAdsApp
from app.services import meta_ads_service as meta
router=APIRouter()

class Config(BaseModel):
    model_config=ConfigDict(extra='forbid')
    verify_token:SecretStr
    accepted_ids:list[str]=Field(min_length=1,max_length=20)

@router.put('/config')
async def configure(request:Request,db=Depends(deps.get_db),actor=Depends(owner)):
    import re
    try:body=Config.model_validate(await request.json())
    except ValueError:raise HTTPException(422,'Configuración de webhook no válida.') from None
    token=body.verify_token.get_secret_value()
    if not 32<=len(token)<=256 or any(not re.fullmatch(r'\d{1,40}',v) for v in body.accepted_ids):raise HTTPException(422,'Usa un verificador de 32 a 256 caracteres e identificadores numéricos.')
    row=db.get(MetaWebhookConfig,1)
    if not row:row=MetaWebhookConfig(id=1,encrypted_verify_token='');db.add(row)
    row.encrypted_verify_token=meta.encrypted(token);row.accepted_ids=json.dumps(sorted(set(body.accepted_ids)));db.commit()
    return {'saved':True,'outbound_enabled':False}

@router.get('/receive')
def verify(request:Request,db=Depends(deps.get_db)):
    params=request.query_params
    mode=params.get('hub.mode');token=params.get('hub.verify_token','');challenge=params.get('hub.challenge','')
    request.scope['query_string']=b''
    row=db.get(MetaWebhookConfig,1)
    if not row or mode!='subscribe' or not hmac.compare_digest(token.encode(),meta.decrypted(row.encrypted_verify_token).encode()) or not challenge or len(challenge)>1024:raise HTTPException(403,'Verificación no válida.')
    return PlainTextResponse(challenge,headers={'Cache-Control':'no-store'})

@router.post('/receive')
async def receive(request:Request,db=Depends(deps.get_db)):
    app=db.get(MetaAdsApp,1);config=db.get(MetaWebhookConfig,1)
    if not app or not config:raise HTTPException(503,'Webhook no configurado.')
    raw=bytearray()
    async for chunk in request.stream():
        raw.extend(chunk)
        if len(raw)>1024*1024:raise HTTPException(413,'Evento demasiado grande.')
    expected='sha256='+hmac.new(meta.decrypted(app.encrypted_secret).encode(),raw,hashlib.sha256).hexdigest()
    if not hmac.compare_digest(request.headers.get('x-hub-signature-256','').encode(),expected.encode()):raise HTTPException(403,'Firma no válida.')
    try:body=json.loads(raw)
    except ValueError:raise HTTPException(400,'Evento no válido.') from None
    if not isinstance(body,dict) or body.get('object') not in ['page','instagram','whatsapp_business_account'] or not isinstance(body.get('entry'),list):raise HTTPException(400,'Estructura de evento no válida.')
    ids=set(json.loads(config.accepted_ids));accepted=[e for e in body['entry'] if isinstance(e,dict) and str(e.get('id')) in ids]
    if not accepted:return {'received':True,'stored':False}
    # Archive only explicitly configured platform assets; no tenant routing inferred.
    payload={'object':body['object'],'entry':accepted};canonical=json.dumps(payload,sort_keys=True,separators=(',',':'));key=hashlib.sha256(canonical.encode()).hexdigest()
    duplicate=db.get(MetaWebhookEvent,key)
    if not duplicate:
        db.add(MetaWebhookEvent(id=key,scope='platform',object_type=body['object'],encrypted_payload=meta.encrypted(canonical),status='received'))
        try:db.commit()
        except IntegrityError:db.rollback()
    return {'received':True,'stored':True}
