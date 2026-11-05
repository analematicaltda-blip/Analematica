"""Tenant/area-scoped semantic layer for institutional BI. No invented measurements."""
from collections import defaultdict
from datetime import datetime,date,time,timedelta,timezone
import hashlib,json,unicodedata
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from sqlalchemy import func,and_,or_
from fastapi import HTTPException
from app.models.tenancy import Inquilino
from app.models.user import Usuario,Alumno,Profesor
from app.models.area import Area
from app.models.academic import Inscripcion,Clase,ProcesoFormacion,Escenario
from app.models.catalog import CatalogoEspecialidad,EmpresaEspecialidad
from app.models.institutional import InstitutionalProcess,EnrollmentEvent
from app.services import workspace_service as ws
from app.services.role_contracts import NAMES,MANAGEMENT,ADMIN_TEAM,contract
UTC=timezone.utc

def vertical(value):
    clean=''.join(c for c in unicodedata.normalize('NFKD',str(value or '').lower()) if not unicodedata.combining(c))
    if clean.startswith(('deport','sport')):return 'deporte'
    if clean.startswith(('cultur','art')):return 'cultura'
    return None

def area_scope(db,user):
    result=set();seen=set();current=user
    for _ in range(8):
        if not current or current.id in seen or current.inquilino_id!=user.inquilino_id:break
        seen.add(current.id);result|={vertical(a.nombre) for a in current.areas if vertical(a.nombre)}
        if result:break
        current=db.get(Usuario,current.reporta_a_usuario_id) if current.reporta_a_usuario_id else None
    return sorted(result)

def context(db,access,role=None,plan=None,tenant_id=None,review=False):
    role=role or next((r for r in ['admin_empresa',*sorted(ADMIN_TEAM),*NAMES] if r in access.roles),None)
    if review:
        if not access.owner:raise HTTPException(403,'La revisión de otros roles está reservada al dueño del sistema.')
        if role not in NAMES or plan not in ['basico','full']:raise HTTPException(422,'Selecciona un rol y un plan válidos para revisión.')
        tenant=db.get(Inquilino,tenant_id) if tenant_id else db.query(Inquilino).filter(Inquilino.activo.is_(True)).order_by(Inquilino.id).first()
        if not tenant or not tenant.activo:raise HTTPException(404,'Entidad no disponible para revisión.')
        permissions={name:bool(plan=='full' and role in MANAGEMENT) for name in ws.PERMISSIONS}
        allowed=['deporte','cultura']
    else:
        if role not in access.roles or role not in NAMES:raise HTTPException(403,'Este rol no pertenece a tu sesión.')
        if tenant_id and tenant_id!=access.tenant.id:raise HTTPException(403,'No puedes cambiar de empresa mediante la URL.')
        tenant=access.tenant;plan=access.caps.canonical_plan;permissions=access.permissions
        allowed=['deporte','cultura'] if role=='admin_empresa' else area_scope(db,access.user) if role in ADMIN_TEAM else []
    return {'review':review,'role':role,'plan':plan,'company':{'id':tenant.id,'name':tenant.nombre_empresa,'tipo_organizacion':tenant.tipo_organizacion,'ambito_organizacional':tenant.ambito_organizacional,'direccion':tenant.direccion,'municipio':tenant.municipio,'pais':tenant.pais},'contract':contract(role,plan),'permissions':permissions,'allowed_verticals':allowed,'full_enabled':bool(permissions.get('crm') or permissions.get('media') or permissions.get('publish') or permissions.get('inbox')),'scope_label':'Revisión del dueño: agregados de la entidad; las sesiones reales se limitan a sus áreas asignadas.' if review else 'Toda la entidad' if role=='admin_empresa' else 'Áreas asignadas: '+(', '.join(allowed) or 'pendientes de asignación'),'refresh_seconds':5}

def bounded_dates(start,end,tz):
    try:zone=ZoneInfo(tz)
    except (ZoneInfoNotFoundError,ValueError):raise HTTPException(422,'Zona horaria no válida.') from None
    if start and end and start>end:raise HTTPException(422,'La fecha inicial supera a la fecha final.')
    begin=datetime.combine(start,time.min,zone).astimezone(UTC) if start else None
    finish=datetime.combine(end+timedelta(days=1),time.min,zone).astimezone(UTC) if end else datetime.now(UTC)
    return begin,finish,zone

def query_rows(db,ctx,finish):
    tenant=ctx['company']['id']
    latest=db.query(EnrollmentEvent.enrollment_id.label('eid'),EnrollmentEvent.status.label('state'),EnrollmentEvent.reason.label('reason'),EnrollmentEvent.effective_at.label('effective'),func.row_number().over(partition_by=EnrollmentEvent.enrollment_id,order_by=(EnrollmentEvent.effective_at.desc(),EnrollmentEvent.id.desc())).label('rank')).filter(EnrollmentEvent.tenant_id==tenant,EnrollmentEvent.effective_at<finish).subquery()
    query=db.query(Inscripcion.id.label('id'),Inscripcion.alumno_id.label('student'),Inscripcion.fecha_inscripcion.label('joined'),Clase.id.label('class_id'),Clase.area.label('area'),Clase.grupo.label('group'),Profesor.id.label('teacher'),Escenario.id.label('venue'),ProcesoFormacion.id.label('process'),ProcesoFormacion.nombre_proceso.label('process_name'),ProcesoFormacion.tipo_proceso.label('process_type'),CatalogoEspecialidad.id.label('specialty'),CatalogoEspecialidad.nombre.label('specialty_name'),CatalogoEspecialidad.vertical.label('vertical'),Alumno.genero.label('gender'),Alumno.grupo_etario.label('age_group'),Alumno.barrio.label('neighborhood'),latest.c.state,latest.c.reason,latest.c.effective)
    query=query.select_from(Inscripcion).join(Alumno,and_(Alumno.id==Inscripcion.alumno_id,Alumno.inquilino_id==tenant)).join(Usuario,and_(Usuario.id==Alumno.usuario_id,Usuario.inquilino_id==tenant)).join(Clase,and_(Clase.id==Inscripcion.clase_id,Clase.inquilino_id==tenant)).outerjoin(Profesor,and_(Profesor.id==Clase.instructor_id,Profesor.inquilino_id==tenant)).outerjoin(Escenario,and_(Escenario.id==Clase.escenario_id,Escenario.inquilino_id==tenant)).outerjoin(ProcesoFormacion,and_(ProcesoFormacion.id==Clase.proceso_id,ProcesoFormacion.inquilino_id==tenant)).outerjoin(InstitutionalProcess,and_(InstitutionalProcess.process_id==ProcesoFormacion.id,InstitutionalProcess.tenant_id==tenant)).outerjoin(CatalogoEspecialidad,and_(CatalogoEspecialidad.id==InstitutionalProcess.specialty_id,or_(CatalogoEspecialidad.es_estandar.is_(True),CatalogoEspecialidad.creado_por_inquilino_id==tenant))).outerjoin(latest,and_(latest.c.eid==Inscripcion.id,latest.c.rank==1)).filter(Inscripcion.inquilino_id==tenant)
    result=[]
    for record in query.all():
        row=record._asdict();scope=vertical(row['area'])
        if ctx['role']!='admin_empresa' and not ctx['review'] and scope not in ctx['allowed_verticals']:continue
        row['vertical']=row['vertical'] or vertical(row['process_type']) or scope
        row['state']=row['state'] or 'sin_clasificar';result.append(row)
    return result

def snapshot(db,ctx,start=None,end=None,tz='UTC',filters=None):
    if ctx['role'] not in MANAGEMENT:raise HTTPException(403,'El contrato de este rol no incluye la analítica institucional de la entidad.')
    begin,finish,zone=bounded_dates(start,end,tz);tenant=ctx['company']['id'];rows=query_rows(db,ctx,finish);filters=filters or {}
    dimensions={'vertical':'vertical','specialty':'specialty','process':'process','teacher':'teacher','venue':'venue','group':'group','gender':'gender','age_group':'age_group','neighborhood':'neighborhood','status':'state'}
    options={key:sorted({str(r[field]) for r in rows if r[field] is not None and str(r[field])!=''}) for key,field in dimensions.items()}
    selected=[]
    for row in rows:
        joined=row['joined'];joined=joined.replace(tzinfo=UTC) if joined and joined.tzinfo is None else joined
        if begin and (joined is None or joined<begin):continue
        if joined and joined>=finish:continue
        if any(value is not None and str(row[dimensions[key]])!=str(value) for key,value in filters.items() if key in dimensions):continue
        selected.append(row)
    adopted=db.query(EmpresaEspecialidad,CatalogoEspecialidad).join(CatalogoEspecialidad).filter(EmpresaEspecialidad.inquilino_id==tenant,EmpresaEspecialidad.activa.is_(True),CatalogoEspecialidad.activo.is_(True)).all()
    adopted=[spec for assoc,spec in adopted if spec.vertical in ctx['allowed_verticals']]
    groups={}
    for spec in adopted:
        if filters.get('vertical') and spec.vertical!=filters['vertical']:continue
        if filters.get('specialty') and str(spec.id)!=str(filters['specialty']):continue
        groups[spec.id]={'id':spec.id,'name':spec.nombre,'vertical':spec.vertical,'students':set(),'enrollments':0,'dropouts':0,'active':0}
    months=defaultdict(lambda:{'enrollments':0,'dropouts':0});states=defaultdict(int)
    for row in selected:
        key=row['specialty'] or 0
        group=groups.setdefault(key,{'id':key,'name':row['specialty_name'] or 'Sin especialidad vinculada','vertical':row['vertical'],'students':set(),'enrollments':0,'dropouts':0,'active':0})
        group['students'].add(row['student']);group['enrollments']+=1;states[row['state']]+=1
        dropout=row['state']=='retirada' and row['reason']=='desercion';group['dropouts']+=int(dropout);group['active']+=int(row['state']=='activa')
        if row['joined']:
            joined=row['joined'].replace(tzinfo=UTC) if row['joined'].tzinfo is None else row['joined'];months[joined.astimezone(zone).strftime('%Y-%m')]['enrollments']+=1
        if dropout and row['effective']:
            event=row['effective'].replace(tzinfo=UTC) if row['effective'].tzinfo is None else row['effective'];months[event.astimezone(zone).strftime('%Y-%m')]['dropouts']+=1
    series=[{**g,'students':len(g['students'])} for g in groups.values()];series.sort(key=lambda g:(-g['students'],g['name']))
    people=len({row['student'] for row in selected});dropouts=sum(g['dropouts'] for g in series)
    teacher_names={str(p.id):u.nombre_completo or u.nombre_usuario for p,u in db.query(Profesor,Usuario).join(Usuario,Profesor.usuario_id==Usuario.id).filter(Profesor.inquilino_id==tenant,Usuario.inquilino_id==tenant).all()}
    venue_names={str(row.id):row.nombre for row in db.query(Escenario).filter_by(inquilino_id=tenant).all()}
    process_names={str(row['process']):row['process_name'] for row in rows if row['process']}
    specialty_names={str(spec.id):spec.nombre for spec in adopted}
    specialty_names.update({str(row['specialty']):row['specialty_name'] for row in rows if row['specialty']})
    quality={'without_status':sum(r['state']=='sin_clasificar' for r in selected),'without_specialty':sum(not r['specialty'] for r in selected),'without_date':sum(r['joined'] is None for r in selected),'excluded_invalid_links':max(0,db.query(Inscripcion).filter_by(inquilino_id=tenant).count()-len(rows)) if ctx['role']=='admin_empresa' or ctx['review'] else None}
    result={'company':ctx['company'],'plan':ctx['plan'],'permissions':ctx['permissions'],'review':ctx['review'],'scope_label':ctx['scope_label'],'kpis':{'students':people,'enrollments':len(selected),'active_enrollments':states['activa'],'dropouts':dropouts,'sports':sum(s.vertical=='deporte' and (not filters.get('vertical') or filters['vertical']=='deporte') and (not filters.get('specialty') or str(s.id)==str(filters['specialty'])) for s in adopted),'cultural':sum(s.vertical=='cultura' and (not filters.get('vertical') or filters['vertical']=='cultura') and (not filters.get('specialty') or str(s.id)==str(filters['specialty'])) for s in adopted),'dropout_rate':round(100*dropouts/len(selected),2) if selected else None},'specialties':series,'states':dict(states),'trend':[{'month':month,**values} for month,values in sorted(months.items())],'quality':quality,'slicers':{key:[{'value':value,'label':({'specialty':specialty_names,'process':process_names,'teacher':teacher_names,'venue':venue_names}.get(key,{}) or {}).get(value,value)} for value in values] for key,values in options.items()},'definition':'Las fechas seleccionan la cohorte por fecha de inscripción. Los estados se evalúan al cierre del periodo. Deserción requiere un retiro explícito con motivo desercion; una cuenta suspendida no se considera deserción. Estudiantes son personas únicas; una persona puede tener varias inscripciones.','updated_at':datetime.now(UTC).isoformat()}
    result['version']=hashlib.sha256(json.dumps({key:value for key,value in result.items() if key!='updated_at'},sort_keys=True,default=str).encode()).hexdigest()
    return result
