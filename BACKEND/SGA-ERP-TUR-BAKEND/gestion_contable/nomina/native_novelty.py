"""Owner-scoped fixed-source intake; records metadata, never a payroll or payment."""
from datetime import date
from decimal import Decimal
import re
from uuid import UUID,uuid5
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import _money,_format_money
from apps.core_erp.outbox_models import OutboxEvent
from . import reviewed_payroll as payroll,reviewed_novelties as sources
from .models import Empleado,ConceptoNomina,NovedadNomina
NS=UUID('859f2558-bbfc-425a-917c-fd6c716f8ec6')
RECORDED='accounting.payroll.native-novelty.recorded.v1'
BOUND='accounting.payroll.native-novelty.bound.v1'
REFERENCE='accounting.payroll.native-novelty.reference.v1'
CORRECTED='accounting.payroll.native-novelty.corrected.v1'
REASONS={'DATA_ENTRY_ERROR','UPDATED_SUPPORT','SOURCE_REVIEW'}
def key(kind,company,value):return uuid5(NS,kind+':'+str(company.pk)+':'+str(value))
def reference(value):
    if not isinstance(value,str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._:-]{0,63}',value):raise AccountingError('Canonical source reference required.')
    return fingerprint(value)
def source_snapshot(row):return {**sources.snapshot(row),'concept_description_digest':fingerprint(row.concepto.descripcion)}
def read(row,company):
    if row is None or row.event_type!=RECORDED or row.domain!='accounting' or row.version!=1 or row.aggregate_root!=str(company.pk) or not isinstance(row.payload,dict) or set(row.payload)!={'body','digest'}:raise AccountingError('Native source proof unavailable.')
    body=row.payload['body']
    if not isinstance(body,dict) or body.get('company_id')!=str(company.pk) or row.pk!=key('record',company,body['request_id']) or fingerprint(body)!=row.payload['digest'] or fingerprint(body['snapshot'])!=body['source_digest']:raise AccountingError('Native source proof changed.')
    return body

def verify_optional(company,row):
    binding=OutboxEvent.objects.filter(pk=key('source',company,row.pk)).first()
    if binding is None:
        if OutboxEvent.objects.filter(event_type=RECORDED,payload__body__company_id=str(company.pk),payload__body__novelty_id=row.pk).exists():raise AccountingError('Native source binding missing; do not adopt as legacy.')
        return None
    if binding.event_type!=BOUND or binding.domain!='accounting' or binding.version!=1 or binding.aggregate_root!=str(company.pk) or not isinstance(binding.payload,dict):raise AccountingError('Native source binding changed.')
    record=OutboxEvent.objects.filter(pk=binding.payload.get('record_id')).first();body=read(record,company)
    expected={'company_id':str(company.pk),'record_id':str(record.pk),'novelty_id':row.pk,'reference_digest':body['reference_digest']}
    claim=OutboxEvent.objects.filter(pk=key('reference',company,body['reference_digest'])).first()
    if binding.payload!=expected or claim is None or claim.event_type!=REFERENCE or claim.domain!='accounting' or claim.version!=1 or claim.aggregate_root!=str(company.pk) or claim.payload!=expected or body['novelty_id']!=row.pk:raise AccountingError('Native source, reference or capture evidence changed.')
    return effective(company,row,body)

def catalog(company,row):
    body=verify_optional(company,row)
    return {'native_source':True,'evidence_digest':body['effective_references']['evidence_digest'],'authorization_digest':body['effective_references']['authorization_digest']} if body else {'native_source':False}

def result(company,sheet,row,body,*,read_only,replayed=False):
    return {'schema':'sgacd-native-payroll-source-v1','company_id':str(company.pk),'payroll_id':str(sheet.pk),'novelty_id':row.pk,'request_id':body['request_id'],'reference_digest':body['reference_digest'],'source':body['effective_snapshot'],'source_digest':fingerprint(body['effective_snapshot']),'revision':body['revision'],'history_digest':body['history_digest'],'history':body['history'],'evidence_digest':body['effective_references']['evidence_digest'],'authorization_digest':body['effective_references']['authorization_digest'],'processed':row.procesada,'found':True,'read_only':read_only,'replayed':replayed,'metadata_written':not read_only and not replayed,'ledger_written':False,'money_transferred':False,'document_uploaded':False,'authorization_independently_verified':False,'confirmations_restored':False}

def missing_reference(company,digest):
    if OutboxEvent.objects.filter(event_type__in=[RECORDED,BOUND],aggregate_root=str(company.pk)).filter(payload__body__reference_digest=digest).exists() or OutboxEvent.objects.filter(event_type=BOUND,aggregate_root=str(company.pk),payload__reference_digest=digest).exists():raise AccountingError('Native reference index missing; no automatic reconstruction.')

@transaction.atomic
def record(*,actor,provider_id,payroll_id,request_id,employee_id,concept_id,event_date,amount,source_reference,evidence_digest,authorization_digest,confirmed):
    user,company,sheet=payroll._context(actor,provider_id,payroll_id);request=str(UUID(str(request_id)));employee=str(UUID(str(employee_id)));digest=reference(source_reference);payroll._digest(evidence_digest);payroll._digest(authorization_digest)
    if confirmed is not True or type(concept_id) is not int or not 1<=concept_id<=9007199254740991:raise AccountingError('Explicit review and concept identity required.')
    parsed=date.fromisoformat(event_date)
    if parsed.isoformat()!=event_date or not sheet.periodo_inicio<=parsed<=sheet.periodo_fin or parsed>timezone.localdate():raise AccountingError('Source date must belong to the payroll and not be future.')
    value=_money(amount)
    if value<=0:raise AccountingError('Positive exact fixed amount required.')
    data={'employee_id':employee,'concept_id':concept_id,'event_date':event_date,'amount':_format_money(value),'reference_digest':digest,'evidence_digest':evidence_digest,'authorization_digest':authorization_digest}
    old=OutboxEvent.objects.filter(pk=key('record',company,request)).first()
    if old:
        body=read(old,company)
        if body['data']!=data or body['actor_id']!=str(user.pk) or body['payroll_id']!=str(sheet.pk):raise AccountingError('Request already bound to other source data.')
        row=NovedadNomina.objects.select_related('concepto').filter(pk=body['novelty_id'],empleado__perfil_id=sheet.perfil_id,planilla=sheet).first()
        if row is None:raise AccountingError('Native source no longer available.')
        body=verify_optional(company,row)
        if body['revision']:raise AccountingError('Source was corrected; recover its current reference instead of replaying capture.')
        return result(company,sheet,row,body,read_only=False,replayed=True)
    if sheet.estado!='BORRADOR' or sheet.asiento_contable_ref_id or sheet.orden_pago_ref_id:raise AccountingError('New sources require an unchanged draft payroll.')
    if OutboxEvent.objects.filter(pk=key('reference',company,digest)).exists():raise AccountingError('Source reference already captured; recover instead of duplicating.')
    missing_reference(company,digest)
    worker=Empleado.objects.select_for_update().filter(pk=employee,perfil_id=sheet.perfil_id,estado='ACTIVO').first();concept=ConceptoNomina.objects.select_for_update().filter(pk=concept_id,tipo__in=['DEVENGADO','DEDUCCION']).first()
    if worker is None or concept is None:raise AccountingError('Active scoped worker and existing supported concept required.')
    row=NovedadNomina.objects.create(planilla=sheet,empleado=worker,concepto=concept,fecha_evento=parsed,valor=Decimal(data['amount']),cantidad=Decimal('1.00'),descripcion='',procesada=False)
    if type(row.pk) is not int or not 1<=row.pk<=9007199254740991:raise AccountingError('Native source identity exceeds supported exact integer range.')
    snap=source_snapshot(row);body={'company_id':str(company.pk),'provider_id':str(sheet.perfil_id),'payroll_id':str(sheet.pk),'actor_id':str(user.pk),'request_id':request,'novelty_id':row.pk,'reference_digest':digest,'data':data,'snapshot':snap,'source_digest':fingerprint(snap)}
    proof=OutboxEvent.objects.create(id=key('record',company,request),event_type=RECORDED,domain='accounting',aggregate_root=str(company.pk),version=1,payload={'body':body,'digest':fingerprint(body)})
    payload={'company_id':str(company.pk),'record_id':str(proof.pk),'novelty_id':row.pk,'reference_digest':digest}
    for kind,event in [('source',BOUND),('reference',REFERENCE)]:OutboxEvent.objects.create(id=key(kind,company,row.pk if kind=='source' else digest),event_type=event,domain='accounting',aggregate_root=str(company.pk),version=1,payload=payload)
    return result(company,sheet,row,verify_optional(company,row),read_only=False)

@transaction.atomic
def lookup(*,actor,provider_id,payroll_id,source_reference):
    _,company,sheet=payroll._context(actor,provider_id,payroll_id);digest=reference(source_reference);claim=OutboxEvent.objects.filter(pk=key('reference',company,digest)).first()
    if claim is None:
        missing_reference(company,digest)
        return {'schema':'sgacd-native-payroll-source-v1','company_id':str(company.pk),'payroll_id':str(sheet.pk),'reference_digest':digest,'found':False,'read_only':True,'metadata_written':False,'ledger_written':False,'money_transferred':False,'document_uploaded':False,'authorization_independently_verified':False,'confirmations_restored':False}
    if claim.event_type!=REFERENCE or claim.domain!='accounting' or claim.version!=1 or claim.aggregate_root!=str(company.pk) or not isinstance(claim.payload,dict):raise AccountingError('Native reference index changed.')
    body=read(OutboxEvent.objects.filter(pk=claim.payload.get('record_id')).first(),company)
    if body['payroll_id']!=str(sheet.pk) or body['reference_digest']!=digest:raise AccountingError('Source belongs to a different payroll.')
    row=NovedadNomina.objects.select_related('concepto').filter(pk=body['novelty_id'],empleado__perfil_id=sheet.perfil_id,planilla=sheet).first()
    if row is None:raise AccountingError('Native source missing.')
    return result(company,sheet,row,verify_optional(company,row),read_only=True)


def effective(company,row,original):
    """Replay bounded immutable corrections; the capture itself never changes."""
    events=list(OutboxEvent.objects.filter(event_type=CORRECTED,aggregate_root=str(row.pk),payload__body__company_id=str(company.pk)).order_by('payload__body__revision')[:21])
    if len(events)>20:raise AccountingError('Native source correction history limit exceeded.')
    current=original['snapshot'];head=fingerprint(original);history=[]
    refs={k:original['data'][k] for k in ['evidence_digest','authorization_digest']}
    for revision,event in enumerate(events,1):
        payload=event.payload
        if not isinstance(payload,dict) or set(payload)!={'body','digest'}:raise AccountingError('Correction proof unavailable.')
        b=payload['body']
        if not isinstance(b,dict) or set(b)!={'company_id','payroll_id','novelty_id','request_id','revision','actor_id','reason_code','evidence_digest','authorization_digest','before','after','previous_digest','data_digest'} or event.domain!='accounting' or event.version!=1 or b.get('revision')!=revision or type(b.get('revision')) is not int or b.get('novelty_id')!=row.pk or b.get('payroll_id')!=original['payroll_id'] or event.pk!=key('correction',company,b['request_id']) or fingerprint(b)!=payload['digest'] or b.get('previous_digest')!=head or b.get('before')!=current or b.get('reason_code') not in REASONS:raise AccountingError('Correction history changed or incomplete.')
        after=b.get('after',{})
        if not isinstance(after,dict) or not {'date','amount'}<=set(after):raise AccountingError('Correction snapshot unavailable.')
        expected={**current,'date':after.get('date'),'amount':after.get('amount')}
        if after!=expected:raise AccountingError('Correction cannot replace a worker, concept or payroll.')
        value=_money(after['amount']);parsed=date.fromisoformat(after['date'])
        if value<=0 or _format_money(value)!=after['amount'] or parsed.isoformat()!=after['date']:raise AccountingError('Correction amount/date changed.')
        refs={k:b[k] for k in ['evidence_digest','authorization_digest']}
        for value in refs.values():payroll._digest(value)
        current=after;head=payload['digest'];history.append(b)
    anchor=OutboxEvent.objects.filter(pk=key('correction-head',company,row.pk)).first()
    if events or anchor is not None:
        if anchor is None or anchor.event_type!='accounting.payroll.native-novelty.head.v1' or anchor.domain!='accounting' or anchor.version!=1 or anchor.aggregate_root!=str(company.pk) or anchor.payload!={'novelty_id':row.pk,'revision':len(history),'digest':head}:raise AccountingError('Correction head missing or history truncated.')
    if source_snapshot(row)!=current:raise AccountingError('Native source differs from its verified history.')
    return {**original,'effective_snapshot':current,'effective_references':refs,'revision':len(history),'history_digest':head,'history':history}

@transaction.atomic
def correct(*,actor,provider_id,payroll_id,novelty_id,request_id,expected_revision,event_date,amount,reason_code,evidence_digest,authorization_digest,confirmed):
    user,company,sheet=payroll._context(actor,provider_id,payroll_id)
    request=str(UUID(str(request_id)))
    if confirmed is not True or type(novelty_id) is not int or not 1<=novelty_id<=9007199254740991 or type(expected_revision) is not int or not 0<=expected_revision<20 or reason_code not in REASONS:raise AccountingError('Explicit correction identity, revision and reason required.')
    payroll._digest(evidence_digest);payroll._digest(authorization_digest)
    parsed=date.fromisoformat(event_date);value=_money(amount)
    if parsed.isoformat()!=event_date or not sheet.periodo_inicio<=parsed<=sheet.periodo_fin or parsed>timezone.localdate() or value<=0:raise AccountingError('Positive exact amount and payroll date required.')
    row=NovedadNomina.objects.select_for_update().select_related('concepto').filter(pk=novelty_id,planilla=sheet,empleado__perfil_id=sheet.perfil_id).first()
    if row is None:raise AccountingError('Scoped native source required.')
    body=verify_optional(company,row)
    if body is None:raise AccountingError('Only captured native sources support this correction protocol.')
    data={'novelty_id':novelty_id,'payroll_id':str(sheet.pk),'expected_revision':expected_revision,'event_date':event_date,'amount':_format_money(value),'reason_code':reason_code,'evidence_digest':evidence_digest,'authorization_digest':authorization_digest,'actor_id':str(user.pk)}
    previous=OutboxEvent.objects.filter(pk=key('correction',company,request)).first()
    if previous is not None:
        b=previous.payload.get('body',{})
        if previous.event_type!=CORRECTED or b.get('data_digest')!=fingerprint(data) or b.get('revision')!=body['revision'] or b not in body['history']:raise AccountingError('Correction request changed or superseded; recover current reference.')
        return {**result(company,sheet,row,body,read_only=False,replayed=True),'correction_request_id':request}
    if sheet.estado!='BORRADOR' or sheet.asiento_contable_ref_id or sheet.orden_pago_ref_id or row.procesada or body['revision']!=expected_revision:raise AccountingError('Correction requires an unprocessed draft and current revision.')
    before=body['effective_snapshot'];after={**before,'date':event_date,'amount':_format_money(value)}
    refs={'evidence_digest':evidence_digest,'authorization_digest':authorization_digest}
    if before==after and refs==body['effective_references']:raise AccountingError('Correction must change amount, date or supporting references.')
    proof={'company_id':str(company.pk),'payroll_id':str(sheet.pk),'novelty_id':row.pk,'request_id':request,'revision':expected_revision+1,'actor_id':str(user.pk),'reason_code':reason_code,**refs,'before':before,'after':after,'previous_digest':body['history_digest'],'data_digest':fingerprint(data)}
    row.fecha_evento=parsed;row.valor=Decimal(_format_money(value));row.save(update_fields=['fecha_evento','valor'])
    OutboxEvent.objects.create(id=key('correction',company,request),event_type=CORRECTED,domain='accounting',aggregate_root=str(row.pk),version=1,payload={'body':proof,'digest':fingerprint(proof)})
    OutboxEvent.objects.update_or_create(id=key('correction-head',company,row.pk),defaults={'event_type':'accounting.payroll.native-novelty.head.v1','domain':'accounting','aggregate_root':str(company.pk),'version':1,'payload':{'novelty_id':row.pk,'revision':expected_revision+1,'digest':fingerprint(proof)}})
    return {**result(company,sheet,row,verify_optional(company,row),read_only=False),'correction_request_id':request}
