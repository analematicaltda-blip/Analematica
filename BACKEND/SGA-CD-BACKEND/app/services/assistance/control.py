"""Two separate, requesting-administrator approvals; agents cannot approve or broaden intent."""
import base64
import hashlib
import hmac
import json
import secrets
import time
import uuid
from urllib.parse import urlsplit
from fastapi import HTTPException
from sqlalchemy import update
from app.models.assistance import ControlPairing,ControlDevice,ControlJob,ControlApproval
from app.models.user import Usuario
from app.models.tenancy import Inquilino
from app.services.assistance import control_crypto as crypto
from app.services.workspace_service import roles_of
from app.services.role_contracts import ADMIN_TEAM

POLICY='sgacd-control-v1'
from pathlib import Path
POLICY_DATA=json.loads(Path(__file__).with_name('control_policy.json').read_text())
HOSTS={key:set(value) for key,value in POLICY_DATA['platform_hosts'].items()}
OPERATIONS=set(POLICY_DATA['operations'])
MUTATIONS={name for name,count in POLICY_DATA['operations'].items() if count==3}
def now():return int(time.time())
def digest(value):return hashlib.sha256(value.encode()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)

def require_staff(db,who):
    user=db.get(Usuario,who.user_id);tenant=db.get(Inquilino,who.tenant_id)
    if not user or not user.activo or user.inquilino_id!=who.tenant_id or not tenant or not tenant.activo or not (roles_of(user)&({'admin_general','admin_empresa'}|ADMIN_TEAM)):
        raise HTTPException(403,'Solo administradores y equipo administrativo activos pueden controlar sus equipos.')
    return who

def device_owned(db,who,identifier):
    value=db.query(ControlDevice).filter_by(id=identifier,user_id=who.user_id,tenant_id=who.tenant_id).first()
    if value is None:raise HTTPException(404,'Equipo no encontrado.')
    return value

def job_owned(db,who,identifier):
    value=db.query(ControlJob).filter_by(id=identifier,user_id=who.user_id,tenant_id=who.tenant_id).first()
    if value is None:raise HTTPException(404,'Operación no encontrada.')
    return value

def pair(db,who,platforms):
    crypto.keys();scopes=sorted(set(platforms))
    if not scopes or any(s not in HOSTS for s in scopes):raise HTTPException(422,'Plataformas no permitidas.')
    code=base64.b32encode(secrets.token_bytes(10)).decode().rstrip('=');identifier=str(uuid.uuid4())
    db.add(ControlPairing(id=identifier,user_id=who.user_id,tenant_id=who.tenant_id,code_hash=digest(code),scopes=canonical(scopes),expires_at=now()+300,used=0));db.commit()
    return {'pairing_code':code,'expires_in':300,'notice':'Introduce el código solo en tu equipo. Vincular no autoriza ninguna acción.'}

def claim(db,code,name,kind='desktop'):
    item=db.query(ControlPairing).filter_by(code_hash=digest(code.strip().upper())).first()
    if not item or item.used or item.expires_at<now():raise HTTPException(401,'Código no válido o vencido.')
    from .engine import Actor
    require_staff(db,Actor(item.user_id,item.tenant_id))
    result=db.execute(update(ControlPairing).where(ControlPairing.id==item.id,ControlPairing.used==0,ControlPairing.expires_at>=now()).values(used=1))
    if result.rowcount!=1:db.rollback();raise HTTPException(409,'El código ya se utilizó.')
    identifier=str(uuid.uuid4());token='device_'+secrets.token_urlsafe(32)
    row=ControlDevice(id=identifier,user_id=item.user_id,tenant_id=item.tenant_id,name=name,kind=kind,token_hash=digest(token),scopes=item.scopes,revoked=0,last_seen=now());db.add(row);db.commit()
    return {'device_id':identifier,'kind':kind,'device_token':token,'server_public_key':crypto.public_key(),'platforms':json.loads(item.scopes),'policy':POLICY,'owner_id':item.user_id,'tenant_id':item.tenant_id}

def authenticate_device(db,token):
    if not token.startswith('device_') or len(token)>200:raise HTTPException(401,'Equipo no autorizado.')
    row=db.query(ControlDevice).filter_by(token_hash=digest(token),revoked=0).first()
    if not row:raise HTTPException(401,'Equipo revocado o no autorizado.')
    from .engine import Actor
    require_staff(db,Actor(row.user_id,row.tenant_id));row.last_seen=now();db.commit();return row

def validate_intent(platform,operation,args):
    if platform not in HOSTS or operation not in OPERATIONS:raise HTTPException(422,'Operación o plataforma no permitida.')
    allowed=set(POLICY_DATA['operation_arguments'][operation])
    if set(args)!=allowed:raise HTTPException(422,'Argumentos incompletos o no permitidos.')
    if any(not isinstance(v,str) or len(v)>4000 or '\x00' in v for v in args.values()):raise HTTPException(422,'Argumento no válido.')
    if operation in {'browser_open','mobile_open_url'}:
        try:
            url=urlsplit(args['url']);port=url.port
        except ValueError:raise HTTPException(422,'URL no válida.') from None
        if url.scheme!='https' or url.hostname not in HOSTS[platform] or port not in (None,443) or url.username or url.password:
            raise HTTPException(422,'Solo se puede abrir el sitio oficial de la plataforma seleccionada.')
        if any(key in url.query.lower() for key in ['access_token','refresh_token','password','client_secret']):raise HTTPException(422,'No se permiten credenciales en URL.')
    if operation in MUTATIONS and operation!='mobile_swipe':
        import re
        if not re.fullmatch(r'[a-z0-9_-]{1,64}',args['ref']) or not re.fullmatch(r'[a-f0-9]{32}',args['observation_id']):raise HTTPException(422,'Referencia de observación no válida.')
    if operation=='browser_press' and args['key'] not in {'Enter','Tab','Escape','ArrowDown','ArrowUp'}:raise HTTPException(422,'Tecla no permitida.')
    if operation in {'browser_fill','mobile_type'}:
        import re
        if re.search(r'(?i)(?:password|contraseña|access_token|refresh_token|api_key|client_secret)\s*[:=]',args['text']):raise HTTPException(422,'No envíes credenciales al control automático.')
    if operation=='browser_upload':
        import re
        if not re.fullmatch(r'[a-f0-9]{64}',args['sha256']) or '/' in args['file'] or '\\' in args['file'] or args['file'].startswith('.'):
            raise HTTPException(422,'El archivo debe seleccionarse en la carpeta compartida local y conservar su hash.')
    if operation=='mobile_swipe':
        import re
        if not re.fullmatch(r'[a-f0-9]{32}',args['observation_id']):raise HTTPException(422,'Observación móvil no válida.')
    if operation=='mobile_swipe' and args['direction'] not in {'up','down','left','right'}:raise HTTPException(422,'Dirección no permitida.')
    canonical(args).encode('utf-8')

def target_allowed(device,platform,operation,args):
    if operation.startswith('mobile_'):
        if device.kind not in {'android','ios'}:raise HTTPException(422,'Esta operación requiere un dispositivo móvil vinculado.')
        allowed=POLICY_DATA['mobile_browsers'][device.kind] if operation=='mobile_open_url' else POLICY_DATA['native_apps'][device.kind][platform]+POLICY_DATA['mobile_browsers'][device.kind]
        if args.get('app_id') not in allowed:raise HTTPException(422,'Aplicación nativa fuera del alcance autorizado.')
    elif operation.startswith('browser_') or operation=='files_list':
        if device.kind!='desktop':raise HTTPException(422,'La operación requiere un ejecutor de escritorio.')
    elif operation=='desktop_status' and device.kind!='desktop':raise HTTPException(422,'El diagnóstico es para escritorio.')

def create_job(db,who,device_id,platform,account,operation,args,purpose):
    device=device_owned(db,who,device_id)
    if device.revoked:raise HTTPException(409,'El equipo fue revocado.')
    if platform not in json.loads(device.scopes):raise HTTPException(403,'La vinculación no incluye esta plataforma.')
    validate_intent(platform,operation,args)
    target_allowed(device,platform,operation,args)
    identifier=str(uuid.uuid4());intent={'policy':POLICY,'target_kind':device.kind,'job_id':identifier,'device_id':device.id,'owner_id':who.user_id,'tenant_id':who.tenant_id,'platform':platform,'account_label':account,'operation':operation,'arguments':args,'purpose':purpose}
    text=canonical(intent);hashed=digest(text);required=3 if operation in MUTATIONS else 2
    row=ControlJob(id=identifier,device_id=device.id,user_id=who.user_id,tenant_id=who.tenant_id,intent=crypto.encrypt(text),digest=hashed,required=required,approvals=0,status='awaiting_review',challenge=crypto.encrypt('REVISADO '+hashed[:10]),expires_at=now()+900,challenge_expires=now()+300,stop_requested=0)
    db.add(row);db.commit();return view(row)

def view(job):
    return {'id':job.id,'device_id':job.device_id,'intent':json.loads(crypto.decrypt(job.intent)),'digest':job.digest,'required_authorizations':job.required,'authorizations':job.approvals,'status':job.status,'expires_at':job.expires_at,'confirmation_phrase':crypto.decrypt(job.challenge) if job.status in {'awaiting_review','awaiting_execution','awaiting_impact'} else None,'stop_requested':bool(job.stop_requested),'result':json.loads(crypto.decrypt(job.result)) if job.result else None,'verification':'device_reported_not_provider_verified'}

def approve(db,who,identifier,stage,hashed,phrase):
    row=job_owned(db,who,identifier);device=device_owned(db,who,row.device_id)
    if device.revoked or row.expires_at<now() or row.challenge_expires<now():raise HTTPException(409,'La autorización venció o el equipo está revocado.')
    if row.stop_requested or row.status not in {'awaiting_review','awaiting_execution','awaiting_impact'} or stage!=row.approvals+1 or stage>row.required:raise HTTPException(409,'La etapa cambió. No se reutilizan autorizaciones.')
    if not hmac.compare_digest(hashed,row.digest) or not hmac.compare_digest(phrase,crypto.decrypt(row.challenge)):raise HTTPException(409,'La confirmación no corresponde al plan revisado.')
    status='approved' if stage==row.required else 'awaiting_execution' if stage==1 else 'awaiting_impact'
    prefix='EJECUTAR ' if stage==1 else 'CONFIRMO IMPACTO '
    challenge=prefix+secrets.token_hex(4).upper() if status!='approved' else ''
    changed=db.execute(update(ControlJob).where(ControlJob.id==row.id,ControlJob.user_id==who.user_id,ControlJob.tenant_id==who.tenant_id,ControlJob.approvals==stage-1,ControlJob.stop_requested==0).values(approvals=stage,status=status,challenge=crypto.encrypt(challenge),challenge_expires=now()+300))
    if changed.rowcount!=1:db.rollback();raise HTTPException(409,'Otra solicitud consumió esta autorización.')
    db.add(ControlApproval(job_id=row.id,stage=stage,user_id=who.user_id,tenant_id=who.tenant_id,digest=row.digest,created_at=now()));db.commit();db.expire_all();return view(job_owned(db,who,identifier))

def begin(db,device,identifier):
    row=db.query(ControlJob).filter_by(id=identifier,device_id=device.id,user_id=device.user_id,tenant_id=device.tenant_id).first()
    if not row:raise HTTPException(404,'Operación no encontrada.')
    if row.status!='approved' or row.stop_requested or device.revoked or row.expires_at<now():raise HTTPException(409,'La operación no tiene autorización ejecutable vigente.')
    intent_text=crypto.decrypt(row.intent);intent=json.loads(intent_text);validate_intent(intent['platform'],intent['operation'],intent['arguments'])
    target_allowed(device,intent['platform'],intent['operation'],intent['arguments'])
    required=3 if intent['operation'] in MUTATIONS else 2
    approvals=db.query(ControlApproval).filter_by(job_id=row.id,user_id=row.user_id,tenant_id=row.tenant_id,digest=row.digest).order_by(ControlApproval.stage).all()
    if row.required!=required or row.approvals!=required or [a.stage for a in approvals]!=list(range(1,required+1)) or digest(intent_text)!=row.digest:raise HTTPException(409,'Las autorizaciones no coinciden con la operación.')
    lease=secrets.token_hex(24);expires=min(row.expires_at,now()+30)
    result=db.execute(update(ControlJob).where(ControlJob.id==row.id,ControlJob.status=='approved',ControlJob.stop_requested==0).values(status='leased',lease_id=lease,lease_expires=expires))
    if result.rowcount!=1:db.rollback();raise HTTPException(409,'La operación ya fue reclamada.')
    db.commit()
    return crypto.sign({'policy':POLICY,'device_id':device.id,'owner_id':device.user_id,'tenant_id':device.tenant_id,'intent_json':intent_text,'digest':row.digest,'lease_id':lease,'issued_at':now(),'expires_at':expires,'approvals':[{'stage':a.stage,'user_id':a.user_id,'tenant_id':a.tenant_id,'digest':a.digest} for a in approvals]})

def report(db,device,identifier,lease,outcome,data):
    row=db.query(ControlJob).filter_by(id=identifier,device_id=device.id,user_id=device.user_id,tenant_id=device.tenant_id).first()
    if not row:raise HTTPException(404,'Operación no encontrada.')
    if row.status not in {'leased','stop_requested'} or not row.lease_id or not hmac.compare_digest(lease,row.lease_id):raise HTTPException(409,'El resultado no corresponde a una ejecución pendiente.')
    text=canonical({'outcome':outcome,'data':data,'stop_requested':bool(row.stop_requested),'provider_success_verified':False})
    if len(text.encode())>32000:raise HTTPException(422,'Resultado demasiado grande.')
    row.status=outcome;row.result=crypto.encrypt(text);db.commit();return {'id':row.id,'status':row.status,'provider_success_verified':False}

def stop(db,who,identifier):
    row=job_owned(db,who,identifier)
    if row.status in {'awaiting_review','awaiting_execution','awaiting_impact','approved'}:row.status='cancelled'
    elif row.status=='leased':row.status='stop_requested'
    row.stop_requested=1;db.commit();return view(row)

def revoke(db,who,identifier):
    row=device_owned(db,who,identifier);row.revoked=1
    for job in db.query(ControlJob).filter_by(device_id=row.id,user_id=who.user_id,tenant_id=who.tenant_id).all():
        if job.status in {'awaiting_review','awaiting_execution','awaiting_impact','approved'}:job.status='cancelled';job.stop_requested=1
        elif job.status=='leased':job.status='stop_requested';job.stop_requested=1
    db.commit();return {'id':row.id,'revoked':True,'notice':'No deshace acciones que ya se entregaron a la plataforma.'}
