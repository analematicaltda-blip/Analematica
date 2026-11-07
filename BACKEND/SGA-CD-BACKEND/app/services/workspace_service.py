"""Authorize every operation from database identity, tenant plan and explicit grants."""
import base64
from dataclasses import dataclass
from datetime import datetime,timezone
import hashlib
import hmac
import json
import os
import re
import uuid

from cryptography.fernet import Fernet,InvalidToken
from fastapi import HTTPException
from sqlalchemy import case,update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
import requests
from app.core.config import settings
from app.models.tenancy import Inquilino
from app.models.billing import Suscripcion,ConsumoInquilino
from app.models.user import Usuario
from app.models.workspace import WorkspaceGrant,WorkspaceAsset,WorkspaceChannel
from app.services.plan_capability_service import PlanCapabilityService,FULL_QUOTAS,normalize_plan_code

from app.services.role_contracts import ADMIN_TEAM
TEAM_ROLES=ADMIN_TEAM
PERMISSIONS={'crm','media','publish','inbox'}

def roles_of(user):
    roles={role.nombre for role in getattr(user,'roles',[]) if getattr(role,'nombre',None)}
    if not roles:
        primary=getattr(user,'rol',None)
        if primary:roles.add(primary.value if hasattr(primary,'value') else str(primary))
    return roles

@dataclass
class Access:
    user:object
    roles:set
    tenant:object
    caps:object
    owner:bool
    permissions:dict
    eligible_full:bool
    @property
    def scope(self):return 'platform' if self.owner else 'tenant:'+str(self.tenant.id)
    @property
    def full(self):return self.eligible_full
    @property
    def manages_team(self):return self.owner or 'admin_empresa' in self.roles
    def require(self,permission):
        if not self.full:raise HTTPException(402,'Esta función requiere Plan Full con suscripción vigente.')
        if not self.permissions.get(permission,False):raise HTTPException(403,'Tu administrador no ha habilitado este permiso para tu cuenta.')

    def require_asset_access(self):
        if not self.full:self.require("media")
        if not any(self.permissions.get(key,False) for key in ["media","publish"]):
            raise HTTPException(403,"Tu administrador no ha habilitado acceso a los archivos multimedia.")

def access_for(db,user):
    if not user.activo:raise HTTPException(403,'Cuenta inactiva.')
    tenant=db.query(Inquilino).filter(Inquilino.id==user.inquilino_id).first()
    if not tenant or not tenant.activo:raise HTTPException(403,'Empresa no disponible o inactiva.')
    roles=roles_of(user);owner='admin_general' in roles
    subscription=db.query(Suscripcion).filter(Suscripcion.inquilino_id==tenant.id).order_by(Suscripcion.id.desc()).first()
    sub={key:getattr(subscription,key,None) for key in ['estado','fecha_fin','fecha_inicio','plan']} if subscription else None
    caps=PlanCapabilityService.resolve_capabilities({'id':tenant.id,'nombre_empresa':tenant.nombre_empresa,'plan':tenant.plan,'activo':tenant.activo},sub)
    starts=getattr(subscription,'fecha_inicio',None)
    if starts and starts.tzinfo is None:starts=starts.replace(tzinfo=timezone.utc)
    begun=starts is None or starts<=datetime.now(timezone.utc)
    full=owner or begun and caps.canonical_plan=='full' and caps.is_active and subscription is not None and normalize_plan_code(subscription.plan)=='full'
    grants={row.permission:row.enabled for row in db.query(WorkspaceGrant).filter(WorkspaceGrant.tenant_id==tenant.id,WorkspaceGrant.user_id==user.id).all()}
    permissions={name:bool(full and (owner or 'admin_empresa' in roles or bool(roles&TEAM_ROLES) and grants.get(name,True))) for name in PERMISSIONS}
    return Access(user,roles,tenant,caps,owner,permissions,bool(full))

def reserve(db,access,key):
    limit=None if access.owner else access.caps.monthly_limits.get(key,0)
    if limit is not None and limit<=0:raise HTTPException(429,'No hay cuota disponible para esta operación.')
    period=datetime.now(timezone.utc).strftime('%Y-%m');capability=('platform_' if access.owner else '')+key
    values=dict(inquilino_id=access.tenant.id,periodo=period,capacidad=capability,cantidad_usada=1)
    dialect=db.get_bind().dialect.name
    insert=pg_insert if dialect=='postgresql' else sqlite_insert if dialect=='sqlite' else None
    if insert is None:raise HTTPException(503,'Motor de cuotas no disponible.')
    statement=insert(ConsumoInquilino).values(**values).on_conflict_do_update(index_elements=['inquilino_id','periodo','capacidad'],set_={'cantidad_usada':ConsumoInquilino.cantidad_usada+1},where=ConsumoInquilino.cantidad_usada<limit if limit is not None else None).returning(ConsumoInquilino.cantidad_usada)
    count=db.execute(statement).scalar_one_or_none();db.commit()
    if count is None:raise HTTPException(429,'Has alcanzado la cuota mensual de esta operación.')
    return (access.tenant.id,period,capability)

def release(db,reservation):
    tenant,period,key=reservation
    db.execute(update(ConsumoInquilino).where(ConsumoInquilino.inquilino_id==tenant,ConsumoInquilino.periodo==period,ConsumoInquilino.capacidad==key).values(cantidad_usada=case((ConsumoInquilino.cantidad_usada>0,ConsumoInquilino.cantidad_usada-1),else_=0)));db.commit()

def worker(path,body=None,method=None):
    url=os.getenv('NODE6_URL','http://node6:8606').rstrip('/')+path
    token=os.getenv('NODE6_TOKEN','')
    if not token:raise HTTPException(503,'El estudio multimedia no está configurado en el servidor.')
    try:
        # Private service-to-service traffic must not traverse the outbound provider proxy.
        with requests.Session() as transport:
            transport.trust_env=False
            response=transport.request(method or ('GET' if body is None else 'POST'),url,json=body,headers={'Authorization':'Bearer '+token},timeout=(10,190),allow_redirects=False)
    except requests.RequestException:raise HTTPException(503,'El estudio no está disponible; inténtalo de nuevo.') from None
    if response.status_code!=200:
        code=response.status_code if response.status_code in [400,409,422,429,503] else 502
        raise HTTPException(code,'El proveedor no pudo completar la operación. Revisa configuración, cuota y conexión; no se mostraron credenciales.')
    return response

def asset_for(db,access,asset_id,kind=None):
    row=db.query(WorkspaceAsset).filter(WorkspaceAsset.id==asset_id,WorkspaceAsset.scope==access.scope).first()
    if not row or kind and row.kind!=kind:raise HTTPException(404,'Archivo no encontrado en tu espacio.')
    return row

def save_asset(db,access,result,kind,title='',commit=True):
    filename=result.get('filename','')
    if not re.fullmatch(r'[a-f0-9]{32}\.(png|mp4|json)',filename) or not filename.endswith({'image':'.png','reel':'.mp4','draft':'.json'}[kind]):raise HTTPException(502,'El estudio devolvió un archivo no válido.')
    row=WorkspaceAsset(id=str(uuid.uuid4()),scope=access.scope,filename=filename,kind=kind,title=title[:120],created_by=access.user.id)
    db.add(row)
    if commit:db.commit()
    else:db.flush()
    return asset_dict(row)

def asset_dict(row):return {'id':row.id,'kind':row.kind,'title':row.title,'created_at':row.created_at.isoformat() if row.created_at else None,'download_url':'/api/v1/workspace/assets/'+row.id+'/download','publish_status':row.publish_status,'video_id':row.publish_video_id}

def encryption():
    key=hmac.new(settings.SECRET_KEY.encode(),b'SGA-CD workspace channel encryption v1',hashlib.sha256).digest()
    return Fernet(base64.urlsafe_b64encode(key))

def channel_credentials(db,access,provider):
    row=db.query(WorkspaceChannel).filter(WorkspaceChannel.scope==access.scope,WorkspaceChannel.provider==provider).first()
    if not row:raise HTTPException(409,'Conecta primero el canal de tu empresa; no se usará el canal de otra organización.')
    try:return json.loads(encryption().decrypt(row.encrypted_credentials.encode()))
    except (InvalidToken,ValueError):raise HTTPException(503,'Debes volver a autorizar este canal.') from None
