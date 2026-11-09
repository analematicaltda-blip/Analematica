"""Provisioned generic-order dispatch with professional attestations and two reviews.

Disabled unless an explicit server policy exists. Checks recorded evidence, not
medical licence authenticity, external work history, or physical service execution.
"""
from datetime import datetime,timezone as dt_timezone,timedelta
from uuid import UUID,uuid5
import re
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied,ValidationError
from apps.audit.models import AuditLog
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.validation import lock_company
from apps.turismo.models import TourismProvider
from apps.turismo.services.company_identity import resolve_company
from apps.prestadores.mi_negocio.gestion_contable.nomina.models import Empleado
from .models import OrdenOperativa
from .state_guard import _permit
from .sg_sst.sargentos import _context
from .sg_sst.access import require_clinical_permission

NS=UUID('45c35413-6b8b-4569-bd9d-bae511b68795')
PREFIX='operational.dispatch.'

def stamp(value):
    if not isinstance(value,str) or len(value)>40:raise ValidationError('Fecha explícita con zona requerida.')
    try:parsed=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError:raise ValidationError('Fecha inválida.') from None
    if timezone.is_naive(parsed):raise ValidationError('Fecha sin zona no admitida.')
    return parsed.astimezone(dt_timezone.utc)

def sha(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise ValidationError('Huella de soporte requerida.')
    return value

def policy(provider):
    catalog=getattr(settings,'OPERATIONAL_DISPATCH_POLICIES',{})
    if not isinstance(catalog,dict):raise ValidationError('Catálogo de políticas no provisionado.')
    raw=catalog.get(str(provider.pk))
    fields={'enabled','version','reviewer_ids','required_ppe','max_shift_minutes','min_rest_minutes','review_ttl_seconds','valid_from','valid_until','evidence_digest'}
    if not isinstance(raw,dict) or set(raw)!=fields or raw['enabled'] is not True:raise ValidationError('Despacho no provisionado; no se habilita por parámetros del solicitante.')
    if (not isinstance(raw['version'],str) or not re.fullmatch('[A-Za-z0-9_.-]{1,40}',raw['version'])
        or not isinstance(raw['reviewer_ids'],list) or not 1<=len(raw['reviewer_ids'])<=10
        or any(not isinstance(x,str) or not re.fullmatch('[1-9][0-9]{0,18}',x) for x in raw['reviewer_ids'])
        or len(set(raw['reviewer_ids']))!=len(raw['reviewer_ids'])
        or not isinstance(raw['required_ppe'],list) or len(raw['required_ppe'])>20
        or any(not isinstance(x,str) or not re.fullmatch('[A-Z0-9_-]{1,30}',x) for x in raw['required_ppe'])
        or len(set(raw['required_ppe']))!=len(raw['required_ppe'])):raise ValidationError('Política y revisores explícitos requeridos.')
    for key,minimum,maximum in [('max_shift_minutes',1,1440),('min_rest_minutes',1,10080),('review_ttl_seconds',30,900)]:
        if type(raw[key]) is not int or not minimum<=raw[key]<=maximum:raise ValidationError('Límites técnicos de política inválidos; no son tasas normativas predeterminadas.')
    sha(raw['evidence_digest']);now=timezone.now()
    if not stamp(raw['valid_from'])<=now<stamp(raw['valid_until']):raise ValidationError('Política no vigente.')
    return {**raw,'reviewer_ids':sorted(raw['reviewer_ids']),'required_ppe':sorted(raw['required_ppe'])}

def owner_context(actor_id,provider_id):
    user,provider=_context(actor_id,provider_id)
    return user,provider,resolve_company(user,provider.pk).tenant

def clinical_context(actor_id,provider_id):
    user=get_user_model().objects.filter(pk=actor_id,is_active=True).first()
    provider=TourismProvider.objects.select_for_update().select_related('owner').filter(pk=provider_id,is_active=True,status='ACTIVE').first()
    if user is None or provider is None or getattr(user,'is_agent',False):raise PermissionDenied('Revisor personal autorizado requerido.')
    terms=policy(provider)
    if str(user.pk) not in terms['reviewer_ids']:raise PermissionDenied('Revisor no provisionado para esta empresa.')
    require_clinical_permission(user,'create')
    company=resolve_company(provider.owner,provider.pk).tenant;lock_company(company.pk);resolve_company(provider.owner,provider.pk)
    return user,provider,company,terms

def order_for(provider,order_id):
    row=OrdenOperativa.objects.select_for_update().filter(pk=UUID(str(order_id)),provider_id=provider.pk,is_active=True).first()
    if row is None:raise ValidationError('Orden activa propia requerida.')
    return row

def source(order):
    return {'order_id':str(order.pk),'provider_id':str(order.provider_id),'contract_id':str(order.contrato_ref_id),
        'start':order.fecha_inicio.isoformat(),'end':order.fecha_fin_estimada.isoformat(),
        'leader_id':str(order.responsable_lider_id) if order.responsable_lider_id else None,
        'projected_cost':format(order.costo_proyectado,'.2f'),'description_digest':fingerprint(order.descripcion_servicio),'active':order.is_active}

def key(kind,body):
    if kind=='attested':return body['order_id']+':'+str(body['revision'])
    if kind in {'reviewed','end-reviewed'}:return fingerprint(body)
    if kind in {'started','ended'}:return body['order_id']
    if kind=='claimed':return body['dispatch_id']+':'+body['employee_id']
    if kind=='released':return body['claim_id']
    if kind=='revoked':return body['attestation_id']
    raise ValidationError('Tipo de evidencia no admitido.')

def identifier(kind,provider,body):return uuid5(NS,kind+':'+str(provider.pk)+':'+key(kind,body))

def save(kind,user,provider,company,order,body):
    body={**body,'provider_id':str(provider.pk),'company_id':str(company.pk),'order_id':str(order.pk),'actor_id':str(user.pk)}
    pk=identifier(kind,provider,body);payload={'body':body,'digest':fingerprint(body)}
    row=OutboxEvent.objects.filter(pk=pk).first()
    if row:
        if row.payload!=payload:raise ValidationError('La evidencia ya existe con otro contenido.')
    else:row=OutboxEvent.objects.create(id=pk,event_type=PREFIX+kind+'.v1',domain='operational',aggregate_root=str(order.pk),payload=payload,version=1)
    return row

def checked(row,kind,provider,company,order):
    if row is None or row.event_type!=PREFIX+kind+'.v1' or row.domain!='operational' or row.aggregate_root!=str(order.pk) or row.version!=1:raise ValidationError('Evidencia operativa no disponible.')
    p=row.payload
    shapes={
        'attested':{'revision','policy','policy_digest','source','source_digest','crew'},
        'reviewed':{'attestation_id','attestation_digest','source_digest','policy_digest','expires_at'},
        'started':{'review_id','review_digest','attestation_id','attestation_digest','source_digest','recorded_start','employee_ids'},
        'claimed':{'employee_id','dispatch_id','dispatch_digest'},
        'released':{'claim_id','claim_digest','end_id','end_digest','actual_end'},
        'revoked':{'attestation_id','attestation_digest'},
        'end-reviewed':{'dispatch_id','dispatch_digest','source_digest','expected_state','actual_end','evidence_digest','expires_at'},
        'ended':{'dispatch_id','dispatch_digest','review_id','review_digest','actual_end','source_digest'},
    }
    if not isinstance(p,dict) or not isinstance(p.get('body'),dict) or set(p['body'])!=shapes[kind]|{'provider_id','company_id','order_id','actor_id'}:raise ValidationError('Contrato de evidencia operativa alterado.')
    if (not isinstance(p,dict) or set(p)!={'body','digest'} or not isinstance(p['body'],dict)
        or p['digest']!=fingerprint(p['body']) or row.pk!=identifier(kind,provider,p['body'])
        or any(p['body'].get(k)!=v for k,v in [('provider_id',str(provider.pk)),('company_id',str(company.pk)),('order_id',str(order.pk))])):raise ValidationError('Evidencia alterada o ajena.')
    return p['body']

def latest_attestation(provider,order):
    return OutboxEvent.objects.filter(event_type=PREFIX+'attested.v1',aggregate_root=str(order.pk),payload__body__provider_id=str(provider.pk)).order_by('-payload__body__revision').first()

def workers(provider,crew):
    from .sg_sst.worker_data_service import resolve_refs
    if not isinstance(crew,list) or not 1<=len(crew)<=10:raise ValidationError('Equipo explícito de1 a10 personas requerido.')
    result=[];seen=set()
    for entry in crew:
        resolve_refs(provider,entry)
        if entry['employee_id'] in seen:raise ValidationError('Trabajador duplicado.')
        seen.add(entry['employee_id'])
        for value in [entry['employee_id'],entry['fitness_authorization_id'],entry['rest_period_id'],*entry['ppe_assignment_ids']]:
            if not isinstance(value,str) or str(UUID(value))!=value:raise ValidationError('Referencias canónicas requeridas.')
        result.append({**entry,'ppe_assignment_ids':sorted(entry['ppe_assignment_ids'])})
    return sorted(result,key=lambda x:x['employee_id'])

@transaction.atomic
def attest(*,actor_id,provider_id,order_id,crew,expected_revision,confirmed):
    user,provider,company,terms=clinical_context(actor_id,provider_id);order=order_for(provider,order_id)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0 or order.estado!='PREPARACION':raise ValidationError('Primera revisión profesional sobre una orden en preparación requerida.')
    previous=latest_attestation(provider,order)
    revision=checked(previous,'attested',provider,company,order)['revision'] if previous else 0
    if expected_revision!=revision:raise ValidationError('Cambió la revisión profesional.')
    row=save('attested',user,provider,company,order,{'revision':revision+1,'policy':terms,'policy_digest':fingerprint(terms),'source':source(order),'source_digest':fingerprint(source(order)),'crew':workers(provider,crew)})
    return {'attestation_id':str(row.pk),'revision':revision+1,'dispatch_recorded':False,'clinical_source_independently_verified':False,'ledger_written':False}

def find_start(provider,order):
    return OutboxEvent.objects.filter(pk=uuid5(NS,'started:'+str(provider.pk)+':'+str(order.pk))).first()

def check_attestation(provider,company,order,terms):
    row=latest_attestation(provider,order);body=checked(row,'attested',provider,company,order)
    if body['policy']!=terms or body['policy_digest']!=fingerprint(terms) or body['source']!=source(order) or body['source_digest']!=fingerprint(source(order)):raise ValidationError('Cambió política u operación; requiere nueva revisión profesional.')
    if OutboxEvent.objects.filter(pk=uuid5(NS,'revoked:'+str(provider.pk)+':'+str(row.pk))).exists():raise ValidationError('Autorización operativa revocada.')
    reviewer=get_user_model().objects.filter(pk=body['actor_id'],is_active=True).first()
    if reviewer is None or getattr(reviewer,'is_agent',False) or str(reviewer.pk) not in terms['reviewer_ids']:raise PermissionDenied('Revisor no vigente.')
    require_clinical_permission(reviewer,'create');crew=workers(provider,body['crew'])
    begin,end=order.fecha_inicio,order.fecha_fin_estimada;now=timezone.now()
    if timezone.is_naive(begin) or timezone.is_naive(end) or not begin<=now<end or end>stamp(terms['valid_until']) or (end-begin).total_seconds()>terms['max_shift_minutes']*60:raise ValidationError('Ventana/jornada fuera de la política explícita.')
    from .sg_sst.worker_data_service import resolve_refs
    for entry in crew:
        facts=resolve_refs(provider,entry)
        if not facts['fitness_fit'] or facts['fitness_from']>begin or facts['fitness_until']<end:raise ValidationError('Falta autorización profesional vigente para toda la operación.')
        equipment=facts['ppe']
        if any(code not in equipment or equipment[code][0]>now or equipment[code][1]<end for code in terms['required_ppe']):raise ValidationError('Falta entrega EPP vigente requerida por política.')
        if facts['rest_end']<begin or facts['rest_end']-facts['rest_start']<timedelta(minutes=terms['min_rest_minutes']) or begin-facts['last_work_end']<timedelta(minutes=terms['min_rest_minutes']):raise ValidationError('Descanso registrado insuficiente o historia posterior incompatible.')
        claims=list(OutboxEvent.objects.filter(event_type=PREFIX+'claimed.v1',payload__body__provider_id=str(provider.pk),payload__body__employee_id=entry['employee_id']).order_by('-created_at')[:101])
        if len(claims)>100:raise ValidationError('Historial requiere conciliación explícita; no se trunca.')
        for claim in claims:
            release=OutboxEvent.objects.filter(pk=uuid5(NS,'released:'+str(provider.pk)+':'+str(claim.pk))).first()
            if release is None:raise ValidationError('Trabajador ya asignado; se exige constancia de finalización, no solo cancelar la orden.')
            other_order=order_for(provider,claim.payload['body']['order_id'])
            cb=checked(claim,'claimed',provider,company,other_order);rb=checked(release,'released',provider,company,other_order)
            ended=OutboxEvent.objects.filter(pk=rb['end_id']).first();ended_body=checked(ended,'ended',provider,company,other_order)
            if rb['end_digest']!=ended.payload['digest'] or rb['actual_end']!=ended_body['actual_end'] or cb['dispatch_id']!=ended_body['dispatch_id']:raise ValidationError('Cierre laboral no corresponde a la asignación.')
            if rb['claim_id']!=str(claim.pk) or rb['claim_digest']!=claim.payload['digest'] or stamp(rb['actual_end'])>facts['last_work_end']:raise ValidationError('Descanso no concuerda con jornadas registradas.')
    return row,body

@transaction.atomic
def review_dispatch(*,actor_id,provider_id,order_id,confirmed):
    user,provider,company=owner_context(actor_id,provider_id);order=order_for(provider,order_id);terms=policy(provider)
    if confirmed is not True or order.estado!='PREPARACION' or find_start(provider,order):raise ValidationError('Primera confirmación del titular y preparación vigentes requeridas.')
    attestation,body=check_attestation(provider,company,order,terms)
    row=save('reviewed',user,provider,company,order,{'attestation_id':str(attestation.pk),'attestation_digest':attestation.payload['digest'],'source_digest':body['source_digest'],'policy_digest':fingerprint(terms),'expires_at':(timezone.now()+timedelta(seconds=terms['review_ttl_seconds'])).isoformat()})
    return {'review_id':str(row.pk),'order_id':str(order.pk),'employee_ids':[x['employee_id'] for x in body['crew']],'recorded_requirements_passed':True,'second_confirmation_required':True,'clinical_content_returned':False,'dispatch_recorded':False,'ledger_written':False}

def result(provider,order,row,replayed=False):
    return {'provider_id':str(provider.pk),'order_id':str(order.pk),'dispatch_id':str(row.pk),'state':order.estado,'dispatch_recorded':True,'replayed':replayed,'physical_service_state_verified':False,'clinical_source_independently_verified':False,'regulatory_verified':False,'ledger_written':False,'money_transferred':False,'confirmations_restored':False}

@transaction.atomic
def apply_dispatch(*,actor_id,provider_id,order_id,review_id,confirmed):
    user,provider,company=owner_context(actor_id,provider_id);order=order_for(provider,order_id)
    if confirmed is not True:raise ValidationError('Segunda confirmación expresa requerida.')
    review=OutboxEvent.objects.filter(pk=UUID(str(review_id))).first();rb=checked(review,'reviewed',provider,company,order)
    if rb['actor_id']!=str(user.pk):raise PermissionDenied('Las dos confirmaciones corresponden al mismo titular.')
    existing=find_start(provider,order)
    if existing:
        body=checked(existing,'started',provider,company,order)
        if body['review_id']!=str(review.pk) or body['review_digest']!=review.payload['digest']:raise ValidationError('Otra revisión originó el inicio registrado.')
        return result(provider,order,existing,True)
    terms=policy(provider)
    if order.estado!='PREPARACION' or stamp(rb['expires_at'])<=timezone.now():raise ValidationError('Revisión vencida o estado modificado.')
    attestation,body=check_attestation(provider,company,order,terms)
    if rb['attestation_id']!=str(attestation.pk) or rb['attestation_digest']!=attestation.payload['digest'] or rb['policy_digest']!=fingerprint(terms) or rb['source_digest']!=fingerprint(source(order)):raise ValidationError('Cambió la evidencia entre confirmaciones.')
    row=save('started',user,provider,company,order,{'review_id':str(review.pk),'review_digest':review.payload['digest'],'attestation_id':str(attestation.pk),'attestation_digest':attestation.payload['digest'],'source_digest':body['source_digest'],'recorded_start':timezone.now().isoformat(),'employee_ids':[x['employee_id'] for x in body['crew']]})
    for entry in body['crew']:save('claimed',user,provider,company,order,{'employee_id':entry['employee_id'],'dispatch_id':str(row.pk),'dispatch_digest':row.payload['digest']})
    token=_permit.set(('OrdenOperativa',str(order.pk),str(provider.pk),'PREPARACION','EJECUCION'))
    try:order.estado='EJECUCION';order.save(update_fields=['estado','updated_at'])
    finally:_permit.reset(token)
    AuditLog.objects.create(user=user,username=user.username,action='OPERATIONAL_DISPATCH_RECORDED',details={'provider_id':str(provider.pk),'operation_id':str(order.pk),'kind':'OrdenOperativa','previous_state':'PREPARACION','new_state':'EJECUCION','dispatch_id':str(row.pk)})
    return result(provider,order,row)

@transaction.atomic
def revoke(*,actor_id,provider_id,order_id,attestation_id,confirmed):
    user,provider,company=owner_context(actor_id,provider_id);order=order_for(provider,order_id)
    if confirmed is not True:raise ValidationError('Revocación explícita requerida.')
    row=OutboxEvent.objects.filter(pk=UUID(str(attestation_id))).first();checked(row,'attested',provider,company,order)
    receipt=save('revoked',user,provider,company,order,{'attestation_id':str(row.pk),'attestation_digest':row.payload['digest']})
    return {'revocation_id':str(receipt.pk),'dispatch_reenabled':False,'physical_containment_verified':False,'ledger_written':False}

@transaction.atomic
def dispatch_state(*,actor_id,provider_id,order_id):
    user,provider,company=owner_context(actor_id,provider_id);order=order_for(provider,order_id);row=find_start(provider,order)
    if row is None:return {'provider_id':str(provider.pk),'order_id':str(order.pk),'state':order.estado,'read_only':True,'dispatch_recorded':False,'confirmations_restored':False,'ledger_written':False}
    body=checked(row,'started',provider,company,order)
    end=OutboxEvent.objects.filter(pk=uuid5(NS,'ended:'+str(provider.pk)+':'+str(order.pk))).first()
    ended=checked(end,'ended',provider,company,order) if end else None
    return {**result(provider,order,row,True),'read_only':True,'source_changed_since_dispatch':body['source_digest']!=fingerprint(source(order)),'end_id':str(end.pk) if end else None,'recorded_end':ended['actual_end'] if ended else None,'completion_accounting_pending':True}

@transaction.atomic
def review_end(*,actor_id,provider_id,order_id,actual_end,evidence_digest,confirmed):
    user,provider,company=owner_context(actor_id,provider_id);order=order_for(provider,order_id)
    if confirmed is not True:raise ValidationError('Primera revisión del fin observado requerida.')
    dispatch=find_start(provider,order);body=checked(dispatch,'started',provider,company,order);end=stamp(actual_end)
    if not stamp(body['recorded_start'])<=end<=timezone.now():raise ValidationError('Fin observado no futuro y posterior al inicio registrado requerido.')
    attestation=OutboxEvent.objects.filter(pk=body['attestation_id']).first();ab=checked(attestation,'attested',provider,company,order)
    row=save('end-reviewed',user,provider,company,order,{'dispatch_id':str(dispatch.pk),'dispatch_digest':dispatch.payload['digest'],'source_digest':fingerprint(source(order)),'expected_state':order.estado,'actual_end':end.isoformat(),'evidence_digest':sha(evidence_digest),'expires_at':(timezone.now()+timedelta(seconds=ab['policy']['review_ttl_seconds'])).isoformat()})
    return {'review_id':str(row.pk),'order_id':str(order.pk),'second_confirmation_required':True,'ledger_written':False,'service_physically_stopped':False}

@transaction.atomic
def apply_end(*,actor_id,provider_id,order_id,review_id,confirmed):
    user,provider,company=owner_context(actor_id,provider_id);order=order_for(provider,order_id)
    if confirmed is not True:raise ValidationError('Segunda confirmación del fin observado requerida.')
    review=OutboxEvent.objects.filter(pk=UUID(str(review_id))).first();rb=checked(review,'end-reviewed',provider,company,order)
    if rb['actor_id']!=str(user.pk):raise PermissionDenied('Mismo titular de las dos revisiones requerido.')
    existing=OutboxEvent.objects.filter(pk=uuid5(NS,'ended:'+str(provider.pk)+':'+str(order.pk))).first()
    if existing:
        eb=checked(existing,'ended',provider,company,order)
        if eb['review_id']!=str(review.pk) or eb['review_digest']!=review.payload['digest']:raise ValidationError('Otra revisión originó el fin registrado.')
        return {'order_id':str(order.pk),'end_id':str(existing.pk),'state':order.estado,'replayed':True,'ledger_written':False,'completion_accounting_pending':True,'physical_service_state_verified':False}
    if stamp(rb['expires_at'])<=timezone.now() or rb['expected_state']!=order.estado or rb['source_digest']!=fingerprint(source(order)):raise ValidationError('Cambió operación o venció la revisión de fin.')
    dispatch=find_start(provider,order);db=checked(dispatch,'started',provider,company,order)
    if rb['dispatch_id']!=str(dispatch.pk) or rb['dispatch_digest']!=dispatch.payload['digest'] or not stamp(db['recorded_start'])<=stamp(rb['actual_end'])<=timezone.now():raise ValidationError('Fin incompatible con el inicio registrado.')
    row=save('ended',user,provider,company,order,{'dispatch_id':str(dispatch.pk),'dispatch_digest':dispatch.payload['digest'],'review_id':str(review.pk),'review_digest':review.payload['digest'],'actual_end':rb['actual_end'],'source_digest':rb['source_digest']})
    for employee in db['employee_ids']:
        claim_id=uuid5(NS,'claimed:'+str(provider.pk)+':'+str(dispatch.pk)+':'+employee)
        claim=OutboxEvent.objects.filter(pk=claim_id).first();cb=checked(claim,'claimed',provider,company,order)
        if cb['dispatch_id']!=str(dispatch.pk) or cb['dispatch_digest']!=dispatch.payload['digest'] or cb['employee_id']!=employee:raise ValidationError('Asignación incompatible con el inicio.')
        save('released',user,provider,company,order,{'claim_id':str(claim.pk),'claim_digest':claim.payload['digest'],'end_id':str(row.pk),'end_digest':row.payload['digest'],'actual_end':rb['actual_end']})
        from .sg_sst.worker_data_service import record_work
        from .sg_sst.worker_data import WorkPeriod
        from django.db.models import Max
        revision=WorkPeriod.objects.filter(provider=provider,employee_id=employee).aggregate(value=Max('revision'))['value'] or 0
        record_work(actor_id=user.pk,provider_id=provider.pk,employee_id=employee,request_id=str(uuid5(NS,'work:'+str(row.pk)+':'+employee)),expected_revision=revision,evidence_digest=rb['evidence_digest'],started_at=db['recorded_start'],ended_at=rb['actual_end'],confirmed=True,operation_reference=str(order.pk),source_kind='DISPATCH')
    before=order.estado
    if before=='EJECUCION':
        target='VALIDACION' if db['source_digest']==fingerprint(source(order)) else 'INCIDENCIA'
        token=_permit.set(('OrdenOperativa',str(order.pk),str(provider.pk),before,target))
        try:order.estado=target;order.save(update_fields=['estado','updated_at'])
        finally:_permit.reset(token)
    AuditLog.objects.create(user=user,username=user.username,action='OPERATIONAL_END_RECORDED',details={'provider_id':str(provider.pk),'operation_id':str(order.pk),'kind':'OrdenOperativa','previous_state':before,'new_state':order.estado,'end_id':str(row.pk)})
    return {'order_id':str(order.pk),'end_id':str(row.pk),'state':order.estado,'replayed':False,'ledger_written':False,'completion_accounting_pending':True,'physical_service_state_verified':False}
