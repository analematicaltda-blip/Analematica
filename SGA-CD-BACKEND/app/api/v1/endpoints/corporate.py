"""Analemática public landing and owner-only management on the existing SGA database."""
import json,re,uuid,html
from datetime import datetime,timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit
from fastapi import APIRouter,Depends,HTTPException,Response
from pydantic import BaseModel,Field,EmailStr,ConfigDict,UUID4
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from app.api import deps
from app.models.corporate import CorporatePage
from app.models.workspace import WorkspaceLead
from app.models.user import Usuario,RolesEnum
from app.services.workspace_service import access_for
router=APIRouter()
SOURCE='Analematica/public-diagnostic'
class Body(BaseModel):model_config=ConfigDict(extra='forbid')
class Content(Body):
    config:dict
    revision:int=Field(ge=0)
class Inquiry(Body):
    request_id:UUID4
    nombre:str=Field(min_length=3,max_length=150)
    entidad:str=Field(min_length=2,max_length=200)
    correo:EmailStr
    telefono:str=Field(min_length=7,max_length=40)
    consent:bool
    website:str=Field(default='',max_length=200)
class Inline(HTMLParser):
    def __init__(self,rich=False):super().__init__(convert_charrefs=True);self.parts=[];self.rich=rich
    def handle_starttag(self,tag,attrs):
        if self.rich and tag in ['span','strong','em','br']:
            self.parts.append('<'+tag+(' class="highlight-cyan"' if tag=='span' else '')+'>')
    def handle_endtag(self,tag):
        if self.rich and tag in ['span','strong','em']:self.parts.append('</'+tag+'>')
    def handle_data(self,data):self.parts.append(html.escape(data) if self.rich else data)
def sanitize(value,path='',depth=0):
    if depth>7:raise HTTPException(422,'Configuración demasiado anidada.')
    if isinstance(value,dict):
        if len(value)>100 or any(k in ['__proto__','constructor','prototype','password','token','api_key','secret','credentials'] or not re.fullmatch(r'[a-zA-Z0-9_]+',k) for k in value):raise HTTPException(422,'Campos no válidos.')
        return {k:sanitize(v,path+'.'+k,depth+1) for k,v in value.items()}
    if isinstance(value,list):
        if len(value)>50:raise HTTPException(422,'Demasiados elementos.')
        return [sanitize(v,path,depth+1) for v in value]
    if not isinstance(value,str) or len(value)>8000:raise HTTPException(422,'Valor de contenido no válido.')
    if path.endswith(('_href','_logo','.url')):
        parsed=urlsplit(value)
        if value.startswith('//') or parsed.scheme not in ['','https','http'] or '\\' in value or any(ord(c)<32 for c in value):raise HTTPException(422,'Enlace no permitido.')
    parser=Inline(rich=path=='.hero.title');parser.feed(value);return ''.join(parser.parts)
def owner(db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)):
    from app.services.corporate_policy import require_owner
    return require_owner(db,user)

from fastapi.security import OAuth2PasswordRequestForm
from app.core.rate_limiter import rate_limit

@router.post('/login',dependencies=[Depends(rate_limit('analematica_login',10,60))])
def login(form:OAuth2PasswordRequestForm=Depends(),db=Depends(deps.get_db)):
    from app.core.security import verify_password,create_access_token
    user=db.query(Usuario).filter(Usuario.nombre_usuario==form.username.strip()).first()
    try:valid=bool(user and verify_password(form.password,user.password_hash))
    except (ValueError,TypeError):valid=False
    if not valid:raise HTTPException(401,'Usuario o contraseña incorrectos.')
    actor=owner(db,user)
    token=create_access_token({'sub':str(user.id),'roles':sorted(actor.roles),'inquilino_id':user.inquilino_id,'nombre_completo':user.nombre_completo})
    return {'access_token':token,'token_type':'bearer','user':{'id':user.id,'name':user.nombre_completo or user.nombre_usuario,'roles':sorted(actor.roles)}}

@router.get('/session')
def private_session(actor=Depends(owner)):
    return {'user':{'id':actor.user.id,'name':actor.user.nombre_completo or actor.user.nombre_usuario,'roles':sorted(actor.roles)},'scope':'platform','console':'analematica'}

@router.get('/config')
def public_config(response:Response,db=Depends(deps.get_db)):
    response.headers['Cache-Control']='no-store';row=db.get(CorporatePage,'analematica')
    return {'config':json.loads(row.payload) if row else {},'revision':row.revision if row else 0}
@router.put('/config')
def save_config(body:Content,db=Depends(deps.get_db),actor=Depends(owner)):
    if len(json.dumps(body.config).encode())>65536:raise HTTPException(413,'Configuración demasiado grande.')
    if set(body.config)-{'header','hero','desafio','filosofia','mision','vision','verticales','adn','impacto','contacto','footer'}:raise HTTPException(422,'Sección de contenido no reconocida.')
    payload=json.dumps(sanitize(body.config),ensure_ascii=False);row=db.get(CorporatePage,'analematica')
    if row:
        found=db.execute(update(CorporatePage).where(CorporatePage.key=='analematica',CorporatePage.revision==body.revision).values(payload=payload,revision=body.revision+1,updated_by=actor.user.id)).rowcount
        if not found:db.rollback();raise HTTPException(409,'Otra sesión actualizó la landing. Recarga antes de publicar.')
    else:
        if body.revision!=0:raise HTTPException(409,'Recarga la configuración antes de publicar.')
        db.add(CorporatePage(key='analematica',payload=payload,updated_by=actor.user.id))
    try:db.commit()
    except IntegrityError:db.rollback();raise HTTPException(409,'Otra sesión publicó primero. Recarga la configuración.') from None
    return {'saved':True,'revision':body.revision+1}
@router.post('/inquiries',status_code=201)
def inquiry(body:Inquiry,db=Depends(deps.get_db)):
    if not body.consent:raise HTTPException(422,'Autoriza el contacto para registrar la solicitud.')
    if not all(value.strip() for value in [body.nombre,body.entidad,body.telefono]):raise HTTPException(422,'Completa tus datos de contacto.')
    if body.website:return {'received':True}
    lead_id=str(body.request_id);existing=db.get(WorkspaceLead,lead_id)
    if existing:
        if existing.scope!='platform':raise HTTPException(409,'No se pudo registrar esta referencia; genera otra solicitud.')
        return {'received':True}
    # Ownership is the platform; public visitors never choose a tenant or impersonate a user.
    from app.models.corporate import CorporateOwner
    binding=db.get(CorporateOwner,1);user=db.get(Usuario,binding.user_id) if binding else None
    if not user or not user.activo:raise HTTPException(503,'El canal de contacto aún no está disponible.')
    notes=json.dumps({'source':SOURCE,'entidad':body.entidad.strip(),'telefono':body.telefono.strip(),'consent':True,'consent_at':datetime.now(timezone.utc).isoformat()},ensure_ascii=False)
    db.add(WorkspaceLead(id=lead_id,scope='platform',name=body.nombre.strip(),email=str(body.correo),stage='nuevo',notes=notes,created_by=user.id))
    try:db.commit()
    except IntegrityError:
        db.rollback()
        if not db.get(WorkspaceLead,lead_id):raise HTTPException(503,'No se pudo registrar la solicitud. Inténtalo de nuevo.') from None
        return {'received':True}
    return {'received':True}
@router.get('/inquiries')
def list_inquiries(db=Depends(deps.get_db),actor=Depends(owner)):
    result=[]
    for row in db.query(WorkspaceLead).filter_by(scope='platform').order_by(WorkspaceLead.created_at.desc()).limit(1000):
        try:metadata=json.loads(row.notes)
        except (ValueError,TypeError):continue
        if not isinstance(metadata,dict) or metadata.get('source')!=SOURCE:continue
        result.append({'id':row.id,'fecha':row.created_at.isoformat() if row.created_at else '', 'nombre':row.name,'correo':row.email,'entidad':metadata.get('entidad',''),'telefono':metadata.get('telefono','')})
    return {'leads':result,'limit':1000}

class Command(Body):
    command:str=Field(min_length=1,max_length=4000)
    target:str=Field(default='sga',pattern=r'^(sga|analematica)$')
    request_id:UUID4

@router.post('/commands')
def commands(body:Command,db=Depends(deps.get_db),actor=Depends(owner)):
    from app.services.corporate_commands import execute
    return execute(db,actor,body.command,body.target,str(body.request_id))

@router.get('/commands')
def command_history(db=Depends(deps.get_db),actor=Depends(owner)):
    from app.models.corporate import CorporateCommand
    return {'commands':[{'id':row.id,'target':row.target,'operation':row.operation,'status':row.status,'undone':bool(row.undone_by),'created_at':row.created_at.isoformat() if row.created_at else None} for row in db.query(CorporateCommand).filter_by(actor_id=actor.user.id).order_by(CorporateCommand.created_at.desc(),CorporateCommand.id.desc()).limit(100)]}

@router.get('/sga-content')
def public_sga_content(response:Response,db=Depends(deps.get_db)):
    from app.services.corporate_commands import FIELDS,Setting
    response.headers['Cache-Control']='no-store'
    return {key:row.value for key in FIELDS.values() if (row:=db.get(Setting,key)) is not None}
