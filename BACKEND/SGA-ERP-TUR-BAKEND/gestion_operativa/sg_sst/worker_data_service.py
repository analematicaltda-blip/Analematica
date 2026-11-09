"""Typed, owner/professional-scoped worker data; never invent missing evidence."""
from uuid import UUID,uuid5
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from django.core.exceptions import ValidationError as ModelValidationError
from rest_framework.exceptions import ValidationError
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Empleado
from .worker_data import ProfessionalAuthorization,PPEAssignment,WorkPeriod,WorkPeriodEnd,RestPeriod,SafetyRevocation

NS=UUID('250814f0-e414-4a08-8ac5-831eb76744f3')
KINDS={'FITNESS':ProfessionalAuthorization,'PPE':PPEAssignment,'WORK':WorkPeriod,'WORK_END':WorkPeriodEnd,'REST':RestPeriod,'REVOKE':SafetyRevocation}

def context(actor_id,provider_id,clinical=False):
    from ..dispatch_authorization import clinical_context,owner_context
    if clinical:
        user,provider,company,_=clinical_context(actor_id,provider_id)
        return user,provider,company
    return owner_context(actor_id,provider_id)

def date(value):
    from ..dispatch_authorization import stamp
    return stamp(value)

def support(value):
    from ..dispatch_authorization import sha
    return sha(value)

def employee(provider,identifier,active=False):
    try:
        if not isinstance(identifier,str) or str(UUID(identifier))!=identifier:raise ValueError()
    except (ValueError,TypeError):raise ValidationError('Trabajador canónico requerido.') from None
    query=Empleado.objects.only('id','perfil_id','estado').filter(pk=identifier,perfil_id=provider.pk)
    if active:query=query.filter(estado='ACTIVO')
    row=query.first()
    if row is None:raise ValidationError('Trabajador de esta empresa requerido.')
    return row

def append(model,user,provider,worker,request_id,expected_revision,evidence_digest,attrs):
    from django.db import connection
    from .worker_data_guards import require
    require(connection)
    if not isinstance(request_id,str) or str(UUID(request_id))!=request_id or type(expected_revision) is not int or expected_revision<0:raise ValidationError('Petición única y revisión esperada explícitas requeridas.')
    support(evidence_digest);pk=uuid5(NS,model.__name__+':'+str(provider.pk)+':'+request_id)
    prior=model.objects.filter(pk=pk).first()
    if prior:
        if prior.provider_id!=provider.pk or prior.employee_id!=worker.pk or prior.recorded_by_id!=user.pk or prior.evidence_digest!=evidence_digest or any(getattr(prior,k)!=v for k,v in attrs.items()):raise ValidationError('La petición ya está ligada a otros datos.')
        return prior,True
    current=model.objects.filter(provider=provider,employee=worker).aggregate(value=Max('revision'))['value'] or 0
    if current!=expected_revision:raise ValidationError('La revisión cambió; recarga los registros.')
    try:row=model.objects.create(id=pk,provider=provider,employee=worker,recorded_by=user,revision=current+1,evidence_digest=evidence_digest,**attrs)
    except ModelValidationError:raise ValidationError('Datos, relaciones o restricciones de seguridad inválidos.') from None
    generated_at=row.recorded_at
    row.refresh_from_db()
    if row.recorded_at!=generated_at or row.provider_id!=provider.pk or row.employee_id!=worker.pk or row.recorded_by_id!=user.pk or row.revision!=current+1 or row.evidence_digest!=evidence_digest or any(getattr(row,k)!=v for k,v in attrs.items()):raise ValidationError('La escritura no conservó la evidencia; se revierte toda la operación.')
    return row,False

def result(row,replayed):return {'record_id':str(row.pk),'employee_id':str(row.employee_id),'provider_id':str(row.provider_id),'revision':row.revision,'recorded_at':row.recorded_at.isoformat(),'replayed':replayed,'clinical_content_returned':False,'source_independently_verified':False,'ledger_written':False}

@transaction.atomic
def record_fitness(*,actor_id,provider_id,employee_id,request_id,expected_revision,evidence_digest,decision,evaluated_at,valid_from,valid_until,document_reference,confirmed):
    user,provider,_=context(actor_id,provider_id,True);worker=employee(provider,employee_id,True)
    if confirmed is not True:raise ValidationError('Confirmación profesional expresa requerida.')
    evaluated,begin,end=date(evaluated_at),date(valid_from),date(valid_until)
    if evaluated>timezone.now() or begin<evaluated or end<=begin or not isinstance(decision,str) or decision not in {'FIT','FIT_RESTRICTED','UNFIT'}:raise ValidationError('Decisión y vigencia profesional explícitas requeridas.')
    ref=UUID(str(document_reference))
    row,replayed=append(ProfessionalAuthorization,user,provider,worker,request_id,expected_revision,evidence_digest,{'decision':decision,'evaluated_at':evaluated,'valid_from':begin,'valid_until':end,'document_reference':ref})
    return result(row,replayed)

@transaction.atomic
def record_ppe(*,actor_id,provider_id,employee_id,request_id,expected_revision,evidence_digest,equipment_code,equipment_reference,quantity,delivered_at,valid_until,confirmed):
    import re
    user,provider,_=context(actor_id,provider_id);worker=employee(provider,employee_id,True)
    if confirmed is not True or not isinstance(equipment_code,str) or not re.fullmatch('[A-Z0-9_-]{1,30}',equipment_code) or type(quantity) is not int or not 1<=quantity<=1000:raise ValidationError('Entrega, código y cantidad enteros explícitos requeridos.')
    begin,end=date(delivered_at),date(valid_until)
    if begin>timezone.now() or end<=begin:raise ValidationError('Entrega observada no futura y vigencia positiva requeridas.')
    row,replayed=append(PPEAssignment,user,provider,worker,request_id,expected_revision,evidence_digest,{'equipment_code':equipment_code,'equipment_reference':UUID(str(equipment_reference)),'quantity':quantity,'delivered_at':begin,'valid_until':end})
    return {**result(row,replayed),'inventory_decremented':False,'physical_delivery_verified':False}

@transaction.atomic
def record_work(*,actor_id,provider_id,employee_id,request_id,expected_revision,evidence_digest,started_at,ended_at,confirmed,operation_reference=None,source_kind='MANUAL'):
    user,provider,_=context(actor_id,provider_id);worker=employee(provider,employee_id)
    if confirmed is not True or source_kind not in {'MANUAL','DISPATCH'}:raise ValidationError('Confirmación de jornada observada requerida.')
    begin=date(started_at);end=date(ended_at) if ended_at is not None else None
    if begin>timezone.now() or end is not None and (end<=begin or end>timezone.now()):raise ValidationError('Jornada observada, ordenada y no futura requerida.')
    operation=UUID(str(operation_reference)) if operation_reference is not None else None
    if operation is not None:
        from ..models import OrdenOperativa
        if not OrdenOperativa.objects.filter(pk=operation,provider_id=provider.pk).exists():raise ValidationError('Referencia operativa ajena.')
    row,replayed=append(WorkPeriod,user,provider,worker,request_id,expected_revision,evidence_digest,{'started_at':begin,'ended_at':end,'operation_reference':operation,'source_kind':source_kind})
    return {**result(row,replayed),'payroll_posted':False,'physical_presence_verified':False}

@transaction.atomic
def close_work(*,actor_id,provider_id,employee_id,request_id,expected_revision,evidence_digest,work_period_id,ended_at,confirmed):
    user,provider,_=context(actor_id,provider_id);worker=employee(provider,employee_id)
    work=WorkPeriod.objects.filter(pk=UUID(str(work_period_id)),provider=provider,employee=worker).first();end=date(ended_at)
    if confirmed is not True or work is None or work.ended_at is not None or end<=work.started_at or end>timezone.now():raise ValidationError('Jornada abierta propia y fin observado válidos requeridos.')
    row,replayed=append(WorkPeriodEnd,user,provider,worker,request_id,expected_revision,evidence_digest,{'work_period':work,'ended_at':end})
    return result(row,replayed)

@transaction.atomic
def record_rest(*,actor_id,provider_id,employee_id,request_id,expected_revision,evidence_digest,started_at,ended_at,confirmed):
    user,provider,_=context(actor_id,provider_id);worker=employee(provider,employee_id)
    begin,end=date(started_at),date(ended_at)
    if confirmed is not True or end<=begin or end>timezone.now():raise ValidationError('Descanso observado, positivo y no futuro requerido.')
    row,replayed=append(RestPeriod,user,provider,worker,request_id,expected_revision,evidence_digest,{'started_at':begin,'ended_at':end})
    return {**result(row,replayed),'physical_rest_verified':False}

@transaction.atomic
def revoke_record(*,actor_id,provider_id,employee_id,request_id,expected_revision,evidence_digest,record_type,record_id,confirmed):
    user,provider,_=context(actor_id,provider_id);worker=employee(provider,employee_id)
    if confirmed is not True or record_type not in {'FITNESS','PPE','REST'}:raise ValidationError('Revocación operativa explícita requerida; no se borran jornadas.')
    record=KINDS[record_type].objects.filter(pk=UUID(str(record_id)),provider=provider,employee=worker).first()
    if record is None:raise ValidationError('Registro propio requerido.')
    row,replayed=append(SafetyRevocation,user,provider,worker,request_id,expected_revision,evidence_digest,{'record_type':record_type,'record_id':record.pk})
    return result(row,replayed)

def revoked(kind,row):return SafetyRevocation.objects.filter(record_type=kind,record_id=row.pk,provider_id=row.provider_id,employee_id=row.employee_id).exists()

def resolve_refs(provider,entry):
    """Internal evaluator: does not return medical decisions to an API client."""
    from ..dispatch_authorization import policy
    from .access import require_clinical_permission
    from django.contrib.auth import get_user_model
    fields={'employee_id','fitness_authorization_id','ppe_assignment_ids','rest_period_id'}
    if not isinstance(entry,dict) or set(entry)!=fields:raise ValidationError('Referencias a autorización, EPP y descanso persistidos requeridas.')
    from django.db import connection
    from .worker_data_guards import require
    require(connection)
    worker=employee(provider,entry['employee_id'],True);terms=policy(provider)
    fitness=ProfessionalAuthorization.objects.filter(pk=UUID(str(entry['fitness_authorization_id'])),provider=provider,employee=worker).first()
    latest=ProfessionalAuthorization.objects.filter(provider=provider,employee=worker).order_by('-revision').first()
    if fitness is None or latest.pk!=fitness.pk or revoked('FITNESS',fitness):raise ValidationError('Autorización actual no disponible.')
    clinician=get_user_model().objects.filter(pk=fitness.recorded_by_id,is_active=True).first()
    if clinician is None or getattr(clinician,'is_agent',False) or str(clinician.pk) not in terms['reviewer_ids']:raise ValidationError('Profesional no vigente.')
    require_clinical_permission(clinician,'create')
    ids=entry['ppe_assignment_ids']
    if not isinstance(ids,list) or len(ids)>20 or len(set(ids))!=len(ids):raise ValidationError('Referencias EPP únicas requeridas.')
    ppe=list(PPEAssignment.objects.filter(pk__in=[UUID(str(x)) for x in ids],provider=provider,employee=worker))
    if len(ppe)!=len(ids) or any(revoked('PPE',row) for row in ppe) or len({row.equipment_code for row in ppe})!=len(ppe):raise ValidationError('Entrega EPP ajena, revocada o duplicada.')
    rest=RestPeriod.objects.filter(pk=UUID(str(entry['rest_period_id'])),provider=provider,employee=worker).first()
    if rest is None or revoked('REST',rest):raise ValidationError('Descanso registrado requerido; no se supone por ausencia de datos.')
    work=list(WorkPeriod.objects.filter(provider=provider,employee=worker,started_at__lte=timezone.now()).order_by('-started_at')[:1001])
    if len(work)>1000:raise ValidationError('Historia requiere conciliación; no se trunca silenciosamente.')
    closures={row.work_period_id:row for row in WorkPeriodEnd.objects.filter(work_period_id__in=[row.pk for row in work if row.ended_at is None])}
    last_end=rest.started_at
    for row in work:
        closure=closures.get(row.pk)
        end=row.ended_at or (closure.ended_at if closure else None)
        if end is None:raise ValidationError('Existe jornada abierta.')
        if row.started_at<rest.ended_at and end>rest.started_at:raise ValidationError('El descanso se superpone a trabajo registrado.')
        last_end=max(last_end,end)
    # Secret medical values stay in memory; only opaque references enter the outbox.
    return {'employee_id':str(worker.pk),'fitness_fit':fitness.decision=='FIT','fitness_from':fitness.valid_from,'fitness_until':fitness.valid_until,'ppe':{row.equipment_code:(row.delivered_at,row.valid_until) for row in ppe},'rest_start':rest.started_at,'rest_end':rest.ended_at,'last_work_end':last_end}
