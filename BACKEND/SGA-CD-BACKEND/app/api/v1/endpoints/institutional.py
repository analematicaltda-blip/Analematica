"""Institutional panels and explicit owner review; URL never upgrades an account."""
from datetime import date,datetime,timezone
import json
from fastapi import APIRouter,Depends,HTTPException,Request
from pydantic import BaseModel,Field,EmailStr,SecretStr,ValidationError
from sqlalchemy import func
from app.api import deps
from app.models.user import Usuario,Role,RolesEnum
from app.models.area import Area
from app.models.tenancy import Inquilino
from app.models.catalog import CatalogoEspecialidad,EmpresaEspecialidad
from app.models.academic import ProcesoFormacion,Clase,Inscripcion
from app.models.institutional import InstitutionalProcess,EnrollmentEvent
from app.services import workspace_service as ws,institutional_service as bi
from app.services.role_contracts import NAMES,MANAGEMENT,ADMIN_TEAM,CREATE,contract
from app.core.security import get_password_hash
router=APIRouter()
class Body(BaseModel):model_config={'extra':'forbid'}
class Profile(Body):
    nombre_empresa:str=Field(min_length=2,max_length=200)
    municipio:str=Field(default='',max_length=150)
    pais:str=Field(default='',max_length=100)
    direccion:str=Field(default='',max_length=250)
class Adopt(Body):ids:list[int]=Field(min_length=1,max_length=1000)
class Mapping(Body):specialty_id:int
class Status(Body):
    status:str=Field(pattern=r'^(activa|retirada|finalizada|pausada)$')
    reason:str=Field(default='no_aplica',pattern=r'^(no_aplica|desercion|traslado|salud|voluntario|otro)$')
    effective_at:datetime|None=None
    note:str=Field(default='',max_length=1000)
class Member(Body):
    name:str=Field(min_length=2,max_length=150)
    email:EmailStr
    password:SecretStr
    role:str
    area_ids:list[int]=Field(default_factory=list,max_length=10)
    supervisor_id:int|None=None

def access(db=Depends(deps.get_db),user=Depends(deps.get_current_active_user)):return ws.access_for(db,user)
def ctx(db,actor,role=None,plan=None,tenant_id=None,review=False):return bi.context(db,actor,role,plan,tenant_id,review)
def require_manager(actor):
    if not (actor.owner or actor.roles&MANAGEMENT):raise HTTPException(403,'Tu contrato no autoriza esta gestión institucional.')

def own_process(db,actor,process_id):
    require_manager(actor);row=db.query(ProcesoFormacion).filter_by(id=process_id,inquilino_id=actor.tenant.id).first()
    if not row:raise HTTPException(404,'Proceso no encontrado en tu entidad.')
    if not (actor.owner or 'admin_empresa' in actor.roles) and bi.vertical(row.tipo_proceso) not in bi.area_scope(db,actor.user):raise HTTPException(403,'El proceso no pertenece a tus áreas asignadas.')
    return row

@router.get('/context')
def context(role:str|None=None,plan:str|None=None,tenant_id:int|None=None,review:bool=False,db=Depends(deps.get_db),actor=Depends(access)):
    return ctx(db,actor,role,plan,tenant_id,review)

@router.get('/entities')
def entities(db=Depends(deps.get_db),actor=Depends(access)):
    if not actor.owner:raise HTTPException(403,'Solo el dueño revisa otras entidades.')
    return {'entities':[{'id':row.id,'name':row.nombre_empresa,'plan':row.plan} for row in db.query(Inquilino).filter(Inquilino.activo.is_(True)).order_by(Inquilino.id).limit(500).all()]}

@router.get('/contracts')
def contracts(db=Depends(deps.get_db),actor=Depends(access)):
    return {'owner':actor.owner,'contracts':[contract(role,plan) for role in NAMES for plan in ['basico','full']],'precedence':'La definición del propietario prevalece: coordinador integra el equipo administrativo Full. El dueño no necesita suscripción.'}

@router.get('/dashboard')
def dashboard(role:str|None=None,plan:str|None=None,tenant_id:int|None=None,review:bool=False,start:date|None=None,end:date|None=None,tz:str='UTC',vertical:str|None=None,specialty:int|None=None,process:int|None=None,teacher:int|None=None,venue:int|None=None,group:str|None=None,gender:str|None=None,age_group:str|None=None,neighborhood:str|None=None,status:str|None=None,db=Depends(deps.get_db),actor=Depends(access)):
    current=ctx(db,actor,role,plan,tenant_id,review)
    return bi.snapshot(db,current,start,end,tz,{key:value for key,value in {'vertical':vertical,'specialty':specialty,'process':process,'teacher':teacher,'venue':venue,'group':group,'gender':gender,'age_group':age_group,'neighborhood':neighborhood,'status':status}.items() if value is not None and value!=''})

@router.put('/profile')
def update_profile(body:Profile,db=Depends(deps.get_db),actor=Depends(access)):
    if not (actor.owner or 'admin_empresa' in actor.roles):raise HTTPException(403,'Solo el administrador de empresa edita sus datos institucionales.')
    if not body.nombre_empresa.strip():raise HTTPException(422,'El nombre de la entidad es obligatorio.')
    for key,value in body.model_dump().items():setattr(actor.tenant,key,value.strip())
    db.commit();return {'saved':True,'name':actor.tenant.nombre_empresa}

@router.get('/catalog')
def catalog(vertical:str|None=None,search:str='',role:str|None=None,plan:str|None=None,tenant_id:int|None=None,review:bool=False,db=Depends(deps.get_db),actor=Depends(access)):
    current=ctx(db,actor,role,plan,tenant_id,review);query=db.query(CatalogoEspecialidad).filter(CatalogoEspecialidad.activo.is_(True)).filter((CatalogoEspecialidad.es_estandar.is_(True))|(CatalogoEspecialidad.creado_por_inquilino_id==current['company']['id']))
    counts={kind:db.query(CatalogoEspecialidad).filter_by(vertical=kind,es_estandar=True,activo=True).count() for kind in ['deporte','cultura']}
    if vertical:
        if vertical not in ['deporte','cultura']:raise HTTPException(422,'Vertical no válida.')
        query=query.filter(CatalogoEspecialidad.vertical==vertical)
    if search:query=query.filter(func.lower(CatalogoEspecialidad.nombre).contains(search.strip().lower(),autoescape=True))
    adopted={row.especialidad_id for row in db.query(EmpresaEspecialidad).filter_by(inquilino_id=current['company']['id'],activa=True).all()}
    return {'counts':counts,'items':[{'id':row.id,'name':row.nombre,'vertical':row.vertical,'category':row.categoria,'adopted':row.id in adopted} for row in query.order_by(CatalogoEspecialidad.nombre).all()],'can_edit':not review and ('admin_empresa' in actor.roles or actor.owner)}

@router.post('/catalog/adopt')
def adopt(body:Adopt,db=Depends(deps.get_db),actor=Depends(access)):
    if not (actor.owner or 'admin_empresa' in actor.roles):raise HTTPException(403,'Solo el administrador selecciona el catálogo de su empresa.')
    selected=db.query(CatalogoEspecialidad).filter(CatalogoEspecialidad.id.in_(set(body.ids)),CatalogoEspecialidad.activo.is_(True),((CatalogoEspecialidad.es_estandar.is_(True))|(CatalogoEspecialidad.creado_por_inquilino_id==actor.tenant.id))).all()
    if len(selected)!=len(set(body.ids)):raise HTTPException(404,'Una especialidad no está disponible para tu entidad.')
    for spec in selected:
        row=db.query(EmpresaEspecialidad).filter_by(inquilino_id=actor.tenant.id,especialidad_id=spec.id).first()
        if row:row.activa=True
        else:db.add(EmpresaEspecialidad(inquilino_id=actor.tenant.id,especialidad_id=spec.id,activa=True))
    db.commit();return {'saved':len(selected)}

@router.get('/processes')
def processes(role:str|None=None,plan:str|None=None,tenant_id:int|None=None,review:bool=False,db=Depends(deps.get_db),actor=Depends(access)):
    current=ctx(db,actor,role,plan,tenant_id,review)
    if current['role'] not in MANAGEMENT:raise HTTPException(403,'Tu contrato no incluye esta gestión.')
    tenant=current['company']['id'];mapping={row.process_id:row.specialty_id for row in db.query(InstitutionalProcess).filter_by(tenant_id=tenant).all()}
    rows=db.query(ProcesoFormacion).filter_by(inquilino_id=tenant).all()
    return {'processes':[{'id':row.id,'name':row.nombre_proceso,'type':row.tipo_proceso,'specialty_id':mapping.get(row.id)} for row in rows if current['review'] or current['role']=='admin_empresa' or bi.vertical(row.tipo_proceso) in current['allowed_verticals']]}

@router.put('/processes/{process_id}')
def map_process(process_id:int,body:Mapping,db=Depends(deps.get_db),actor=Depends(access)):
    row=own_process(db,actor,process_id)
    spec=db.query(EmpresaEspecialidad).filter_by(inquilino_id=actor.tenant.id,especialidad_id=body.specialty_id,activa=True).first()
    if not spec:raise HTTPException(404,'Primero selecciona esta especialidad en el catálogo de tu entidad.')
    selected=db.get(CatalogoEspecialidad,body.specialty_id)
    if bi.vertical(row.tipo_proceso) and selected.vertical!=bi.vertical(row.tipo_proceso):raise HTTPException(422,'La especialidad no corresponde al tipo deportivo o cultural del proceso.')
    mapping=db.query(InstitutionalProcess).filter_by(tenant_id=actor.tenant.id,process_id=process_id).first()
    if mapping is None:mapping=InstitutionalProcess(tenant_id=actor.tenant.id,process_id=process_id);db.add(mapping)
    mapping.specialty_id=body.specialty_id;mapping.recorded_by=actor.user.id;db.commit();return {'saved':True}

@router.get('/enrollments')
def enrollments(role:str|None=None,plan:str|None=None,tenant_id:int|None=None,review:bool=False,db=Depends(deps.get_db),actor=Depends(access)):
    current=ctx(db,actor,role,plan,tenant_id,review)
    if current['role'] not in MANAGEMENT:raise HTTPException(403,'Tu contrato no incluye registros institucionales.')
    rows=bi.query_rows(db,current,datetime.now(timezone.utc))
    return {'enrollments':[{'id':row['id'],'student_id':row['student'],'process':row['process_name'],'class_id':row['class_id'],'specialty':row['specialty_name'],'state':row['state'],'reason':row['reason']} for row in rows[-500:]],'total':len(rows),'limit':500}

@router.post('/enrollments/{enrollment_id}/status')
def enrollment_status(enrollment_id:int,body:Status,db=Depends(deps.get_db),actor=Depends(access)):
    require_manager(actor);row=db.query(Inscripcion).filter_by(id=enrollment_id,inquilino_id=actor.tenant.id).first()
    if not row:raise HTTPException(404,'Inscripción no encontrada en tu entidad.')
    lesson=db.query(Clase).filter_by(id=row.clase_id,inquilino_id=actor.tenant.id).first()
    if not lesson:raise HTTPException(409,'La inscripción requiere una clase válida antes de clasificar su estado.')
    if not (actor.owner or 'admin_empresa' in actor.roles) and bi.vertical(lesson.area) not in bi.area_scope(db,actor.user):raise HTTPException(403,'La inscripción no pertenece a tus áreas.')
    instant=body.effective_at or datetime.now(timezone.utc)
    if instant.tzinfo is None or instant>datetime.now(timezone.utc):raise HTTPException(422,'La fecha efectiva debe incluir zona horaria y no puede ser futura.')
    joined=row.fecha_inscripcion
    if joined and instant<(joined.replace(tzinfo=timezone.utc) if joined.tzinfo is None else joined):raise HTTPException(422,'El estado no puede anteceder a la inscripción.')
    if body.status=='retirada' and body.reason=='no_aplica' or body.status!='retirada' and body.reason!='no_aplica':raise HTTPException(422,'Selecciona un motivo de retiro solo para una inscripción retirada.')
    db.add(EnrollmentEvent(tenant_id=actor.tenant.id,enrollment_id=row.id,status=body.status,reason=body.reason,effective_at=instant,recorded_by=actor.user.id,note=body.note));db.commit();return {'saved':True}

@router.get('/team')
def team(db=Depends(deps.get_db),actor=Depends(access)):
    require_manager(actor);roles=actor.roles;own=actor.owner or 'admin_empresa' in roles;allowed=CREATE['admin_empresa'] if own else list({r for role in roles for r in CREATE.get(role,[])})
    members=[]
    for user in db.query(Usuario).filter_by(inquilino_id=actor.tenant.id).all():
        if not own and not set(bi.area_scope(db,user))&set(bi.area_scope(db,actor.user)):continue
        actual_roles=sorted(ws.roles_of(user));role=next((r for r in NAMES if r in actual_roles),None)
        if role:members.append({'id':user.id,'name':user.nombre_completo or user.nombre_usuario,'roles':actual_roles,'group':contract(role,actor.caps.canonical_plan)['group'],'plan':actor.caps.canonical_plan,'full_administrative':bool(actor.full and role in MANAGEMENT),'active':user.activo,'supervisor_id':user.reporta_a_usuario_id,'areas':[a.nombre for a in user.areas]})
    return {'members':members,'creatable_roles':allowed,'areas':[{'id':area.id,'name':area.nombre} for area in db.query(Area).all() if bi.vertical(area.nombre)],'plan':actor.caps.canonical_plan}

@router.post('/team',status_code=201)
async def create_member(request:Request,db=Depends(deps.get_db),actor=Depends(access)):
    require_manager(actor)
    try:
        body=Member.model_validate(await request.json());password=body.password.get_secret_value()
        if not 12<=len(password.encode())<=72:raise ValueError()
    except (ValidationError,ValueError):raise HTTPException(422,'Revisa los datos. La contraseña debe ocupar entre 12 y 72 bytes; no se devolvieron sus valores.') from None
    allowed=CREATE['admin_empresa'] if actor.owner or 'admin_empresa' in actor.roles else {r for role in actor.roles for r in CREATE.get(role,[])}
    if body.role not in allowed:raise HTTPException(403,'Tu contrato no permite crear este rol.')
    email=str(body.email).lower()
    if db.query(Usuario).filter((func.lower(Usuario.correo)==email)|(func.lower(Usuario.nombre_usuario)==email)).first():raise HTTPException(409,'Ese correo ya está registrado.')
    supervisor=db.get(Usuario,body.supervisor_id or actor.user.id)
    if not supervisor or supervisor.inquilino_id!=actor.tenant.id or not supervisor.activo:raise HTTPException(404,'El superior no pertenece a tu entidad activa.')
    areas=db.query(Area).filter(Area.id.in_(set(body.area_ids))).all()
    if len(areas)!=len(set(body.area_ids)) or any(not bi.vertical(area.nombre) for area in areas):raise HTTPException(422,'Área no válida.')
    if not (actor.owner or 'admin_empresa' in actor.roles) and any(bi.vertical(a.nombre) not in bi.area_scope(db,actor.user) for a in areas):raise HTTPException(403,'No puedes asignar áreas fuera de tu competencia.')
    user=Usuario(inquilino_id=actor.tenant.id,nombre_usuario=email,correo=email,nombre_completo=body.name.strip(),password_hash=get_password_hash(password),rol=RolesEnum(body.role),activo=True,reporta_a_usuario_id=supervisor.id)
    role=db.query(Role).filter_by(nombre=body.role).one();user.roles=[role];user.areas=areas;db.add(user);db.flush()
    # Keep the role-specific identity rows required by the original operational modules.
    from app.models.user import Profesor,Alumno,JefeArea,Coordinador,JefeAlmacen,Almacenista,JefeEscenarios
    detail={'profesor':Profesor,'alumno':Alumno,'jefe_area':JefeArea,'coordinador':Coordinador,'jefe_almacen':JefeAlmacen,'almacenista':Almacenista,'jefe_escenarios':JefeEscenarios}.get(body.role)
    if detail:db.add(detail(usuario_id=user.id,inquilino_id=actor.tenant.id))
    db.commit();return {'created':True,'id':user.id,'username':email,'role':body.role,'organization_plan':actor.caps.canonical_plan}

class Assignment(Body):
    area_ids:list[int]=Field(default_factory=list,max_length=10)
    supervisor_id:int|None=None

@router.put('/team/{user_id}/assignment')
def assign_member(user_id:int,body:Assignment,db=Depends(deps.get_db),actor=Depends(access)):
    if not (actor.owner or 'admin_empresa' in actor.roles):raise HTTPException(403,'Solo el administrador de empresa asigna las áreas y jerarquía de su equipo.')
    user=db.query(Usuario).filter_by(id=user_id,inquilino_id=actor.tenant.id).first()
    if not user or ws.roles_of(user)&{'admin_general','admin_empresa'}:raise HTTPException(404,'Selecciona un miembro administrativo u operativo de tu entidad.')
    areas=db.query(Area).filter(Area.id.in_(set(body.area_ids))).all()
    if len(areas)!=len(set(body.area_ids)) or any(not bi.vertical(area.nombre) for area in areas):raise HTTPException(422,'Área no válida.')
    supervisor=db.get(Usuario,body.supervisor_id or actor.user.id)
    if not supervisor or supervisor.inquilino_id!=actor.tenant.id or not supervisor.activo:raise HTTPException(404,'Superior no válido en esta entidad.')
    seen={user.id};current=supervisor
    while current:
        if current.id in seen:raise HTTPException(422,'La asignación crearía un ciclo en la jerarquía.')
        seen.add(current.id);current=db.get(Usuario,current.reporta_a_usuario_id) if current.reporta_a_usuario_id else None
    user.areas=areas;user.reporta_a_usuario_id=supervisor.id;db.commit();return {'saved':True}

@router.delete('/team/{user_id}/permissions-overrides')
def inherit_permissions(user_id:int,db=Depends(deps.get_db),actor=Depends(access)):
    if not (actor.owner or 'admin_empresa' in actor.roles):raise HTTPException(403,'Solo el administrador restaura los permisos heredados.')
    user=db.query(Usuario).filter_by(id=user_id,inquilino_id=actor.tenant.id).first()
    if not user or not ws.roles_of(user)&ADMIN_TEAM:raise HTTPException(404,'Selecciona un miembro del equipo administrativo.')
    from app.models.workspace import WorkspaceGrant
    db.query(WorkspaceGrant).filter_by(tenant_id=actor.tenant.id,user_id=user.id).delete();db.commit();return {'saved':True,'full_active':actor.full}
