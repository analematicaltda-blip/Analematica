"""Existing fixed deduction sources -> reviewed payroll -> atomic consumption.
No inference from quantity units, clinical data, legal eligibility or consent hashes.
"""
from uuid import UUID,uuid5
from django.db.models import Q
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import _money,_format_money
from apps.core_erp.outbox_models import OutboxEvent
from .models import NovedadNomina
NS=UUID('fac8333b-dff9-4b11-b01c-b59021803c66')
KIND='accounting.payroll.novelty-consumed.v1'
MODE='FIXED_LIABILITY_FROM_SOURCE'
COMPENSATION_MODE='COMPENSATION_FROM_SOURCE'
EARNING_FIELDS={'bonificaciones','comisiones'}
def earning_rules(values):
    if not isinstance(values,list) or not 1<=len(values)<=8:raise AccountingError('One to8 explicit earning concept classifications required.')
    seen=set()
    for row in values:
        if not isinstance(row,dict) or set(row)!={'concept_id','detail_field'} or type(row['concept_id']) is not int or not 1<=row['concept_id']<=9007199254740991 or row['concept_id'] in seen or row['detail_field'] not in EARNING_FIELDS:raise AccountingError('Unique concept identity and bonus/commission classification required.')
        seen.add(row['concept_id'])
    return sorted(values,key=lambda r:r['concept_id'])
def key(company,identifier):return uuid5(NS,str(company.pk)+':'+str(identifier))
def snapshot(row):
    return {'novelty_id':row.pk,'employee_id':str(row.empleado_id),'payroll_id':str(row.planilla_id) if row.planilla_id else None,'date':row.fecha_evento.isoformat() if row.fecha_evento else None,'concept_id':row.concepto_id,'concept_code':row.concepto.codigo,'concept_kind':row.concepto.tipo,'quantity':format(row.cantidad,'.2f'),'amount':format(row.valor,'.2f'),'description_digest':fingerprint(row.descripcion)}
def pending(employee,payroll):return NovedadNomina.objects.filter(empleado=employee).filter(Q(planilla=payroll)|Q(planilla__isnull=True))
def calculate(company,payroll,employee,values,digest,*,earning_rules=None):
    if not isinstance(values,list) or len(values)>8:raise AccountingError('Up to8 reviewed source deductions per worker required.')
    ids=[]
    for value in values:
        if not isinstance(value,dict) or set(value)!={'novelty_id','evidence_digest','authorization_digest'} or type(value['novelty_id']) is not int or not 1<=value['novelty_id']<=9007199254740991 or value['novelty_id'] in ids:raise AccountingError('Explicit unique source deduction identity and references required.')
        digest(value['evidence_digest']);digest(value['authorization_digest']);ids.append(value['novelty_id'])
    sources=list(pending(employee,payroll).select_for_update().select_related('concepto').order_by('pk')[:9])
    if len(sources)>8 or {r.pk for r in sources}!=set(ids):raise AccountingError('Review every pending source for this worker; no novelty may be omitted or injected.')
    references={v['novelty_id']:v for v in values};rows=[];total=0;earnings={r['concept_id']:r['detail_field'] for r in earning_rules or []}
    for source in sources:
        from .native_novelty import verify_optional
        native=verify_optional(company,source)
        if native and any(references[source.pk][k]!=native['effective_references'][k] for k in ['evidence_digest','authorization_digest']):raise AccountingError('Native source support references changed.')
        if source.procesada or (source.concepto.tipo!='DEDUCCION' and not(source.concepto.tipo=='DEVENGADO' and source.concepto_id in earnings)) or source.cantidad!=1 or source.fecha_evento is None or not payroll.periodo_inicio<=source.fecha_evento<=payroll.periodo_fin:raise AccountingError('Unprocessed dated fixed-amount deduction with quantity1 required; unsupported novelties require separate review.')
        try:amount=_money(format(source.valor,'.2f'))
        except ValueError:raise AccountingError('Positive exact source deduction amount required.') from None
        if amount<=0 or OutboxEvent.objects.filter(pk=key(company,source.pk)).exists():raise AccountingError('Source amount must be positive and not previously consumed.')
        body=snapshot(source);item={**references[source.pk],'source':body,'source_digest':fingerprint(body),'amount':_format_money(amount),'authorization_independently_verified':False}
        if source.concepto.tipo=='DEVENGADO':item['earning_field']=earnings[source.concepto_id]
        else:total+=amount
        rows.append(item)
    return rows,total

def coverage(payroll,workers):
    ids={d['novelty_id'] for w in workers for d in w.get('novelty_items',w.get('novelty_deductions',[]))}
    assigned=set(NovedadNomina.objects.filter(planilla=payroll).values_list('pk',flat=True))
    if assigned-ids:raise AccountingError('Assigned payroll novelties omitted from worker selection.')

def consume(company,payroll,review,journal,workers):
    coverage(payroll,workers)
    for worker in workers:
        for d in worker.get('novelty_items',worker.get('novelty_deductions',[])):
            row=NovedadNomina.objects.select_for_update().select_related('concepto').filter(pk=d['novelty_id'],empleado_id=worker['employee_id'],empleado__perfil_id=payroll.perfil_id).first()
            if row is None or row.procesada or snapshot(row)!=d['source'] or OutboxEvent.objects.filter(pk=key(company,row.pk)).exists():raise AccountingError('Novelty changed or consumed after review.')
            row.planilla=payroll;row.procesada=True;row.save(update_fields=['planilla','procesada'])
            OutboxEvent.objects.create(id=key(company,row.pk),event_type=KIND,domain='accounting',aggregate_root=str(payroll.pk),version=1,payload={'company_id':str(company.pk),'payroll_id':str(payroll.pk),'review_id':str(review.pk),'journal_id':str(journal.pk),'source_digest':d['source_digest'],'novelty_id':row.pk})

def verify(company,payroll,review,journal,workers):
    coverage(payroll,workers)
    for worker in workers:
        for d in worker.get('novelty_items',worker.get('novelty_deductions',[])):
            row=NovedadNomina.objects.select_related('concepto').filter(pk=d['novelty_id'],empleado_id=worker['employee_id'],empleado__perfil_id=payroll.perfil_id).first();claim=OutboxEvent.objects.filter(pk=key(company,d['novelty_id'])).first()
            from .native_novelty import verify_optional
            if row is not None:verify_optional(company,row)
            expected={'company_id':str(company.pk),'payroll_id':str(payroll.pk),'review_id':str(review.pk),'journal_id':str(journal.pk),'source_digest':d['source_digest'],'novelty_id':d['novelty_id']}
            if row is None or not row.procesada or row.planilla_id!=payroll.pk or fingerprint(d['source'])!=d['source_digest'] or snapshot(row)!={**d['source'],'payroll_id':str(payroll.pk)} or claim is None or claim.event_type!=KIND or claim.domain!='accounting' or claim.version!=1 or claim.aggregate_root!=str(payroll.pk) or claim.payload!=expected:raise AccountingError('Consumed payroll novelty or its proof changed; reconcile instead of replaying.')
