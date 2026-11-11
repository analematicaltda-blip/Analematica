"""Reviewed analytical attribution of already-posted payroll to recorded work.
No new expense, statutory rates, payroll dispersal or operational completion.
"""
from datetime import datetime,time,timedelta
from zoneinfo import ZoneInfo
from uuid import UUID,uuid5
from django.db import transaction,connection
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import _money,_format_money
from apps.core_erp.outbox_models import OutboxEvent
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data import WorkPeriod,WorkPeriodEnd
from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data_guards import require as require_guards
from apps.prestadores.mi_negocio.gestion_operativa.models import OrdenOperativa
from . import reviewed_payroll as payroll_engine
import re

NS=UUID('1d741b2d-b967-43b3-a15d-f67d431cb341')
REVIEW='accounting.payroll-cost.reviewed.v1'
RECORDED='accounting.payroll-cost.recorded.v1'
BOGOTA=ZoneInfo('America/Bogota')

def micros(delta):return (delta.days*86400+delta.seconds)*1000000+delta.microseconds

def split_cents(total,weights):
    """Largest remainder, with UUID ascending tie-break and unallocated last."""
    if type(total) is not int or total<0 or not weights or any(type(v) is not int or v<0 for v in weights.values()) or sum(weights.values())<=0:raise AccountingError('Nonnegative exact cost and positive declared capacity required.')
    denominator=sum(weights.values());parts={k:total*v//denominator for k,v in weights.items()}
    ordered=sorted(weights,key=lambda k:(-(total*weights[k]%denominator),k=='UNALLOCATED',k))
    for key in ordered[:total-sum(parts.values())]:parts[key]+=1
    return parts

def latest(kind,company,payroll):return OutboxEvent.objects.filter(event_type=kind,aggregate_root=str(payroll.pk),payload__company_id=str(company.pk)).order_by('-payload__revision').first()

def checked(row,kind,company,payroll):
    if row is None or row.event_type!=kind or row.domain!='accounting' or row.version!=1 or row.aggregate_root!=str(payroll.pk) or set(row.payload)!={'company_id','revision','body','digest'}:raise AccountingError('Cost allocation proof missing or incompatible.')
    body=row.payload['body']
    if not isinstance(body,dict) or body.get('company_id')!=str(company.pk) or body.get('payroll_id')!=str(payroll.pk) or type(body.get('revision')) is not int or body['revision']<1 or row.payload['revision']!=body['revision'] or row.payload['company_id']!=str(company.pk) or fingerprint(body)!=row.payload['digest'] or row.pk!=uuid5(NS,kind+':'+str(payroll.pk)+':'+str(body['revision'])):raise AccountingError('Cost allocation evidence changed.')
    return body

def save(kind,body):return OutboxEvent.objects.create(id=uuid5(NS,kind+':'+body['payroll_id']+':'+str(body['revision'])),event_type=kind,domain='accounting',aggregate_root=body['payroll_id'],payload={'company_id':body['company_id'],'revision':body['revision'],'body':body,'digest':fingerprint(body)},version=1)

def payroll_source(company,payroll):
    review=payroll_engine._latest(payroll)
    if review is None:raise AccountingError('Reviewed and posted payroll required.')
    applied=payroll_engine._verified_applied(company,payroll,review)
    if applied is None:raise AccountingError('Payroll must be posted before analytical attribution.')
    return review,review.payload['review']['snapshot'],applied

def verify_dispatch(company,provider,row,orders,end):
    if row.source_kind!='DISPATCH':return
    from apps.prestadores.mi_negocio.gestion_operativa import dispatch_authorization as dispatch
    from apps.prestadores.mi_negocio.gestion_operativa.sg_sst.worker_data_service import NS as WORK_NS
    order=orders.get(str(row.operation_reference))
    if order is None:raise AccountingError('Recorded dispatch operation required.')
    started=dispatch.find_start(provider,order);sb=dispatch.checked(started,'started',provider,company,order)
    ended=OutboxEvent.objects.filter(pk=uuid5(dispatch.NS,'ended:'+str(provider.pk)+':'+str(order.pk))).first();eb=dispatch.checked(ended,'ended',provider,company,order)
    expected_request=str(uuid5(dispatch.NS,'work:'+str(ended.pk)+':'+str(row.employee_id)))
    expected_id=uuid5(WORK_NS,'WorkPeriod:'+str(provider.pk)+':'+expected_request)
    if str(row.employee_id) not in sb['employee_ids'] or eb['dispatch_id']!=str(started.pk) or eb['dispatch_digest']!=started.payload['digest'] or row.pk!=expected_id or row.started_at!=dispatch.stamp(sb['recorded_start']) or end!=dispatch.stamp(eb['actual_end']):raise AccountingError('Work period does not match the recorded dispatch/end.')

def work_records(payroll,employees):
    start=datetime.combine(payroll.periodo_inicio,time.min,BOGOTA);end=datetime.combine(payroll.periodo_fin+timedelta(days=1),time.min,BOGOTA)
    records=list(WorkPeriod.objects.filter(provider_id=payroll.perfil_id,employee_id__in=employees,started_at__lt=end).annotate(effective_end=Coalesce('ended_at','closing__ended_at')).filter(Q(effective_end__isnull=True)|Q(effective_end__gt=start)).order_by('employee_id','started_at','pk')[:101])
    if len(records)>100:raise AccountingError('Narrow the source period; at most100 overlapping work records are supported.')
    return records

def calculate(user,company,payroll,capacities,operation_centers):
    require_guards(connection);review,snapshot,applied=payroll_source(company,payroll)
    if applied['reversed']:raise AccountingError('A reversed payroll cannot support effective operational costs.')
    workers={r['employee_id']:r for r in snapshot['workers']}
    if not isinstance(capacities,list) or not 1<=len(capacities)<=10 or not isinstance(operation_centers,dict) or len(operation_centers)>20:raise AccountingError('Bounded explicit paid capacity and operation centers required.')
    start=datetime.combine(payroll.periodo_inicio,time.min,BOGOTA);end=datetime.combine(payroll.periodo_fin+timedelta(days=1),time.min,BOGOTA)
    capacity={}
    for row in capacities:
        if not isinstance(row,dict) or set(row)!={'employee_id','capacity_seconds'} or not isinstance(row['employee_id'],str) or str(UUID(row['employee_id']))!=row['employee_id'] or row['employee_id'] not in workers or row['employee_id'] in capacity or type(row['capacity_seconds']) is not int or not 0<row['capacity_seconds']<=micros(end-start)//1000000:raise AccountingError('Unique payroll employee and declared paid seconds within period required.')
        capacity[row['employee_id']]=row['capacity_seconds']*1000000
    if set(capacity)!=set(workers):raise AccountingError('Declare capacity for every posted payroll employee; never drop an employee from the denominator.')
    records=work_records(payroll,workers)
    closures={r.work_period_id:r for r in WorkPeriodEnd.objects.filter(work_period_id__in=[r.pk for r in records if r.ended_at is None])}
    operation_ids={str(r.operation_reference) for r in records if r.operation_reference}
    if not operation_ids or set(operation_centers)!=operation_ids:raise AccountingError('Every recorded operation needs one explicit center; extra/missing operations are not inferred.')
    for key,code in operation_centers.items():
        if str(UUID(key))!=key or not isinstance(code,str) or not re.fullmatch('[A-Z0-9][A-Z0-9_.-]{0,39}',code):raise AccountingError('Canonical operation and explicit center code required.')
    orders={str(r.pk):r for r in OrdenOperativa.objects.filter(provider_id=payroll.perfil_id,pk__in=operation_ids)}
    if set(orders)!=operation_ids:raise AccountingError('An operation is foreign or unavailable.')
    # Version 2 binds the business reference and operation window, not just its UUID.
    # These references are declared contract/package links, never proof of a sale.
    operation_sources=[{'operation_id':str(order.pk),'commercial_reference_id':str(order.contrato_ref_id),
        'planned_start':order.fecha_inicio.isoformat(),'planned_end':order.fecha_fin_estimada.isoformat(),
        'description_digest':fingerprint(order.descripcion_servicio),'active':order.is_active}
        for _,order in sorted(orders.items())]
    if any(not row['active'] for row in operation_sources):raise AccountingError('Inactive operation cannot support current costs.')
    provider=payroll_engine.TourismProvider.objects.select_related('owner').get(pk=payroll.perfil_id)
    intervals={key:[] for key in workers};weights={key:{} for key in workers};source=[]
    for record in records:
        closed=closures.get(record.pk);finish=record.ended_at or (closed.ended_at if closed else None)
        if finish is None or finish<=record.started_at or finish>timezone.now():raise AccountingError('Close every overlapping work period with observed nonfuture data before attributing costs.')
        if closed and (closed.provider_id!=payroll.perfil_id or closed.employee_id!=record.employee_id):raise AccountingError('Work closure scope mismatch.')
        clipped_start=max(record.started_at,start);clipped_end=min(finish,end);duration=micros(clipped_end-clipped_start)
        if duration<=0:raise AccountingError('Invalid work/period intersection.')
        identifier=str(record.employee_id);intervals[identifier].append((clipped_start,clipped_end));operation=str(record.operation_reference) if record.operation_reference else 'UNALLOCATED_WORK'
        weights[identifier][operation]=weights[identifier].get(operation,0)+duration
        if record.source_kind not in {'MANUAL','DISPATCH'}:raise AccountingError('Unsupported work evidence kind.')
        verify_dispatch(company,provider,record,orders,finish)
        source.append({'work_id':str(record.pk),'employee_id':identifier,'operation_id':str(record.operation_reference) if record.operation_reference else None,'source_kind':record.source_kind,'started_at':record.started_at.isoformat(),'ended_at':finish.isoformat(),'closure_id':str(closed.pk) if closed else None,'duration_us':duration,'evidence_digest':record.evidence_digest,'recorded_by':str(record.recorded_by_id),'closure_evidence_digest':closed.evidence_digest if closed else None,'closure_recorded_by':str(closed.recorded_by_id) if closed else None})
    allocations=[];unallocated=[];coverage=[];totals={k:0 for k in ['salary','employer','provisions']}
    for identifier,worker in sorted(workers.items()):
        spans=sorted(intervals[identifier])
        if any(left[1]>right[0] for left,right in zip(spans,spans[1:])):raise AccountingError('Overlapping work cannot be counted twice.')
        measured=sum(weights[identifier].values())
        if measured>capacity[identifier]:raise AccountingError('Recorded work exceeds declared paid capacity; reconcile hours/overtime instead of hiding it.')
        op_weights={key:value for key,value in weights[identifier].items() if key!='UNALLOCATED_WORK'}
        assigned=sum(op_weights.values());op_weights['UNALLOCATED']=capacity[identifier]-assigned
        coverage.append({'employee_id':identifier,'declared_paid_capacity_us':capacity[identifier],'recorded_work_us':measured,'assigned_work_us':assigned,'recorded_unassigned_work_us':weights[identifier].get('UNALLOCATED_WORK',0),'missing_capacity_evidence_us':capacity[identifier]-measured})
        parts={kind:split_cents(_money(worker[field]),op_weights) for kind,field in [('salary','gross' if 'gross' in worker else 'base'),('employer','employer'),('provisions','provisions')]}
        for kind,field in [('salary','gross' if 'gross' in worker else 'base'),('employer','employer'),('provisions','provisions')]:totals[kind]+=_money(worker[field])
        for operation in sorted(op_weights):
            row={'employee_id':identifier,'operation_id':None if operation=='UNALLOCATED' else operation,'center_code':None if operation=='UNALLOCATED' else operation_centers[operation],'allocation_weight_us':op_weights[operation],'amounts':{kind:_format_money(value[operation]) for kind,value in parts.items()}}
            row['total_cost']=_format_money(sum(value[operation] for value in parts.values()))
            (unallocated if operation=='UNALLOCATED' else allocations).append(row)
    return {'schema':'sgacd-payroll-operation-cost-v2','company_id':str(company.pk),'provider_id':str(payroll.perfil_id),'payroll_id':str(payroll.pk),'payroll_review_id':str(review.pk),'payroll_review_digest':review.payload['review_digest'],'journal_id':applied['journal_id'],'since':snapshot['since'],'until':snapshot['until'],'timezone':'America/Bogota','allocation_basis':'OWNER_DECLARED_PAID_CAPACITY_US','rounding':'LARGEST_REMAINDER_UUID_UNALLOCATED_LAST','capacities':sorted(capacities,key=lambda r:r['employee_id']),'operation_centers':operation_centers,'operation_sources':operation_sources,'work_source':source,'coverage':coverage,'allocations':allocations,'unallocated':unallocated,'posted_cost':{kind:_format_money(value) for kind,value in totals.items()},'posted_total_cost':_format_money(sum(totals.values())),'source_independently_verified':False,'statutory_payroll_rules_verified':False}

@transaction.atomic
def review_costs(*,actor,provider_id,payroll_id,capacities,operation_centers,evidence_digest,reason_code,expected_revision,confirmed):
    user,company,payroll=payroll_engine._context(actor,provider_id,payroll_id)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0 or not isinstance(reason_code,str) or not re.fullmatch('[A-Z0-9_-]{1,40}',reason_code):raise AccountingError('Explicit first cost review, reason and revision required.')
    payroll_engine._digest(evidence_digest);preview=calculate(user,company,payroll,capacities,operation_centers)
    old=latest(REVIEW,company,payroll);previous=checked(old,REVIEW,company,payroll)['revision'] if old else 0
    if expected_revision!=previous:raise AccountingError('Cost review changed; reload before proposing another revision.')
    body={'company_id':str(company.pk),'payroll_id':str(payroll.pk),'provider_id':str(payroll.perfil_id),'revision':previous+1,'reviewed_by':str(user.pk),'preview':preview,'evidence_digest':evidence_digest,'reason_code':reason_code,'expires_at':(timezone.now()+timedelta(minutes=15)).isoformat()}
    row=save(REVIEW,body)
    return {'company_id':str(company.pk),'payroll_id':str(payroll.pk),'review_id':str(row.pk),'revision':body['revision'],'preview':preview,'ledger_written':False,'allocation_recorded':False,'money_transferred':False}

def verified_record(company,payroll,row):
    body=checked(row,RECORDED,company,payroll);review=OutboxEvent.objects.filter(pk=body['review_id']).first();reviewed=checked(review,REVIEW,company,payroll)
    if body['review_digest']!=review.payload['digest'] or body['revision']!=reviewed['revision'] or body['posting_date']!=reviewed['preview']['until'] or body['provider_id']!=str(payroll.perfil_id):raise AccountingError('Recorded cost/review link changed.')
    return body,reviewed

def is_current(user,company,payroll,preview):
    from rest_framework.exceptions import ValidationError
    from django.core.exceptions import ValidationError as ModelValidationError
    try:return calculate(user,company,payroll,preview['capacities'],preview['operation_centers'])==preview
    except (AccountingError,ValueError,TypeError,ValidationError,ModelValidationError):return False

@transaction.atomic
def record_costs(*,actor,provider_id,payroll_id,review_id,confirmed):
    user,company,payroll=payroll_engine._context(actor,provider_id,payroll_id)
    if confirmed is not True:raise AccountingError('Second explicit cost confirmation required.')
    review=latest(REVIEW,company,payroll);body=checked(review,REVIEW,company,payroll)
    if str(review.pk)!=str(UUID(str(review_id))) or body['reviewed_by']!=str(user.pk):raise AccountingError('Current review by the same owner required.')
    old=OutboxEvent.objects.filter(pk=uuid5(NS,RECORDED+':'+str(payroll.pk)+':'+str(body['revision']))).first()
    if old:
        recorded,reviewed=verified_record(company,payroll,old)
        return {'company_id':str(company.pk),'payroll_id':str(payroll.pk),'allocation_id':str(old.pk),'revision':body['revision'],'replayed':True,'ledger_written':False,'allocation_recorded':True,'money_transferred':False,'confirmations_restored':False,'source_current':is_current(user,company,payroll,reviewed['preview'])}
    if datetime.fromisoformat(body['expires_at'])<=timezone.now():raise AccountingError('Cost review expired.')
    preview=calculate(user,company,payroll,body['preview']['capacities'],body['preview']['operation_centers'])
    if preview!=body['preview']:raise AccountingError('Payroll, work records or attribution changed after review.')
    row=save(RECORDED,{'company_id':str(company.pk),'payroll_id':str(payroll.pk),'revision':body['revision'],'review_id':str(review.pk),'review_digest':review.payload['digest'],'recorded_by':str(user.pk),'posting_date':preview['until'],'provider_id':str(payroll.perfil_id)})
    return {'company_id':str(company.pk),'payroll_id':str(payroll.pk),'allocation_id':str(row.pk),'revision':body['revision'],'replayed':False,'ledger_written':False,'allocation_recorded':True,'money_transferred':False,'confirmations_restored':False,'source_current':True}

@transaction.atomic
def cost_state(*,actor,provider_id,payroll_id):
    user,company,payroll=payroll_engine._context(actor,provider_id,payroll_id);review=latest(REVIEW,company,payroll);record=latest(RECORDED,company,payroll)
    reviewed=checked(review,REVIEW,company,payroll) if review else None;recorded=None
    if record:
        result,origin=verified_record(company,payroll,record)
        current=is_current(user,company,payroll,origin['preview'])
        recorded={'allocation_id':str(record.pk),'revision':result['revision'],'preview':origin['preview'],'source_current':current,'effective_for_current_source':current}
    return {'company_id':str(company.pk),'payroll_id':str(payroll.pk),'read_only':True,'review':{'review_id':str(review.pk),'revision':reviewed['revision'],'preview':reviewed['preview'],'expires_at':reviewed['expires_at']} if review else None,'recorded':recorded,'ledger_written':False,'money_transferred':False,'confirmations_restored':False}

@transaction.atomic
def cost_sources(*,actor,provider_id,payroll_id):
    user,company,payroll=payroll_engine._context(actor,provider_id,payroll_id);require_guards(connection)
    review,snapshot,applied=payroll_source(company,payroll)
    from .models import Empleado
    names={str(row.pk):row.nombre+' '+row.apellido for row in Empleado.objects.filter(perfil_id=payroll.perfil_id,pk__in=[r['employee_id'] for r in snapshot['workers']])}
    records=work_records(payroll,names);ids={r.operation_reference for r in records if r.operation_reference}
    orders=list(OrdenOperativa.objects.filter(provider_id=payroll.perfil_id,pk__in=ids).order_by('pk'))
    return {'company_id':str(company.pk),'provider_id':str(payroll.perfil_id),'payroll_id':str(payroll.pk),'read_only':True,'payroll_reversed':applied['reversed'],'journal_id':applied['journal_id'],'workers':[{'employee_id':row['employee_id'],'name':names[row['employee_id']],'salary':row.get('gross',row['base']),'employer':row['employer'],'provisions':row['provisions'],'reviewed_payroll_center':row['cost_center']} for row in snapshot['workers']],
        'work':[{'work_id':str(r.pk),'employee_id':str(r.employee_id),'operation_id':str(r.operation_reference) if r.operation_reference else None,'started_at':r.started_at.isoformat(),'ended_at':r.effective_end.isoformat() if r.effective_end else None,'source_kind':r.source_kind} for r in records],
        'operations':[{'operation_id':str(r.pk),'label':r.descripcion_servicio[:80],'state':r.estado} for r in orders],'ledger_written':False,'clinical_content_returned':False,'capacity_inferred':False}

@transaction.atomic
def operation_cost_report(*,actor,provider_id,order_id,since,until):
    from apps.prestadores.mi_negocio.gestion_operativa.dispatch_authorization import owner_context
    from .models import Planilla
    from datetime import date
    user,provider,company=owner_context(getattr(actor,'pk',None),provider_id)
    start,end=date.fromisoformat(since),date.fromisoformat(until)
    if start.isoformat()!=since or end.isoformat()!=until or start>end or (end-start).days>366:raise AccountingError('Bounded canonical financial posting-date interval required.')
    identifier=str(UUID(str(order_id)))
    if not OrdenOperativa.objects.filter(pk=identifier,provider_id=provider.pk).exists():raise AccountingError('Own operation required.')
    records=list(OutboxEvent.objects.filter(event_type=RECORDED,payload__company_id=str(company.pk),payload__body__posting_date__gte=since,payload__body__posting_date__lte=until).order_by('aggregate_root','-payload__revision')[:1001])
    if len(records)>1000:raise AccountingError('Narrow the reporting interval; at most1000 allocation revisions are supported.')
    selected={}
    for record in records:selected.setdefault(record.aggregate_root,record)
    payrolls={str(r.pk):r for r in Planilla.objects.filter(pk__in=selected,perfil_id=provider.pk)}
    rows=[];total=0;incomplete=[]
    for payroll_id,record in selected.items():
        payroll=payrolls.get(payroll_id)
        if payroll is None:raise AccountingError('Allocation payroll is unavailable in this company.')
        proof,origin=verified_record(company,payroll,record);preview=origin['preview']
        allocation=[r for r in preview['allocations'] if r['operation_id']==identifier]
        current=is_current(user,company,payroll,preview)
        if not allocation and current:continue
        amount=sum(_money(r['total_cost']) for r in allocation)
        if current:total+=amount
        else:incomplete.append(str(record.pk))
        rows.append({'allocation_id':str(record.pk),'payroll_id':payroll_id,'journal_id':preview['journal_id'],'posting_date':proof['posting_date'],'revision':proof['revision'],'source_current':current,'cost':_format_money(amount),'centers':sorted({r['center_code'] for r in allocation})})
    missing=list(Planilla.objects.filter(perfil_id=provider.pk,asiento_contable_ref_id__isnull=False,periodo_fin__gte=start,periodo_fin__lte=end).exclude(pk__in=selected).values_list('pk',flat=True)[:101])
    if len(missing)>100:raise AccountingError('Narrow the interval; too many payrolls await cost attribution.')
    complete=not incomplete and not missing
    return {'schema':'sgacd-operation-labor-cost-v1','company_id':str(company.pk),'provider_id':str(provider.pk),'operation_id':identifier,'since':since,'until':until,'date_basis':'PAYROLL_LEDGER_POSTING_DATE','currency':'COP','read_only':True,'source_complete':complete,'known_current_cost':_format_money(total),'total_cost':_format_money(total) if complete else None,'unqualified_allocations':incomplete,'unallocated_payrolls':[str(pk) for pk in missing],'lines':rows,'ledger_written':False,'money_transferred':False,'operational_cost_field_overwritten':False,'other_costs_included':False,'physical_execution_verified':False}
