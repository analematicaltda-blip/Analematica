"""Explicit human-reviewed accrual for delivered services, not invoice acceptance.
Two separate owner confirmations; no inference of delivery from a booking alone.
"""
import re
from decimal import Decimal, localcontext
from datetime import date
from uuid import UUID,uuid5
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from apps.core_erp.accounting.models import Account,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from .reservation_fiscal import locked_source,latest_review,validated_review,digest

REVIEW='accounting.reservation.recognition-reviewed.v1'
POSTED='accounting.reservation.recognized.v1'
NAMESPACE=UUID('39825e48-7428-496b-af78-eb90507d6425')

def evidence(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise ValidationError('Se requiere huella de evidencia SHA-256.')
    return value

def key(source):return 'reservation-recognition:'+str(source.pk)

def latest(company,source):
    return OutboxEvent.objects.filter(event_type=REVIEW,aggregate_root=str(source.pk),payload__company_id=str(company.pk)).order_by('-payload__revision').first()

def accounts(company,mapping,tax):
    if not isinstance(mapping,dict) or set(mapping)!={'receivable','revenue','tax_liability'}:raise ValidationError('Selecciona las tres funciones contables explícitas.')
    expected={'receivable':'ASSET','revenue':'REVENUE','tax_liability':'LIABILITY'};result={};seen=set()
    for role,kind in expected.items():
        value=mapping[role]
        if role=='tax_liability' and value is None and tax=='0.00':continue
        identifier=UUID(str(value))
        row=Account.plain_objects.select_related('chart_of_accounts').filter(pk=identifier,tenant_id=company.pk,is_active=True,type=kind,chart_of_accounts__tenant_id=company.pk).first()
        if row is None or identifier in seen:raise ValidationError('Cuenta incompatible, ajena, duplicada o inactiva.')
        seen.add(identifier);result[role]=row
    return result

ADVANCE_APPLIED='accounting.reservation.advance-applied.v1'

def advance_claim_id(journal_id):
    return uuid5(NAMESPACE,'advance:'+str(journal_id))

def validated_advance(company,source,allocation,day):
    """Owner-attested allocation of one whole posted receipt; never creates cash.

    Company lock is held by locked_source. A deterministic claim prevents this
    receipt being allocated twice, including after reversal of recognition.
    Partial splitting and automatic bank reconciliation are intentionally absent.
    """
    if source.deposit_paid==0:
        if allocation is not None:raise ValidationError('La reserva no declara anticipo.')
        return None
    if not isinstance(allocation,dict) or set(allocation)!={'journal_id','liability_account_id','evidence_digest'}:
        raise ValidationError('Conciliación del anticipo: indica asiento previo, pasivo y soporte revisado.')
    if not Decimal('0')<source.deposit_paid<=source.total_price:raise ValidationError('Anticipo incompatible con el total de la reserva.')
    journal=JournalEntry.plain_objects.select_for_update().filter(pk=UUID(str(allocation['journal_id'])),tenant=company,is_posted=True,is_reversal=False,hash_version='v2',base_currency='COP').first()
    if journal is None or journal.date>day or journal.compute_hash()!=journal.system_hash or JournalEntry.plain_objects.filter(tenant=company,reversed_entry_id=journal.pk,is_posted=True).exists():
        raise ValidationError('El anticipo requiere un asiento íntegro, vigente y anterior al reconocimiento.')
    from apps.core_erp.accounting.fx_settlement import protect_cash_reversal
    from apps.core_erp.accounting.exceptions import AccountingError
    try:protect_cash_reversal(company,journal)
    except AccountingError:raise ValidationError('El recibo tiene una liquidación FX activa o evidencia incompatible; no puede aplicarse dos veces.') from None
    lines=list(LedgerEntry.plain_objects.filter(journal_entry=journal,tenant=company).select_related('account__chart_of_accounts'))
    if len(lines)!=2:raise ValidationError('Solo se admite un recibo simple completo, sin fraccionar ni inferir saldos.')
    credits=[line for line in lines if line.credit_amount==source.deposit_paid and line.debit_amount==0 and line.account.type=='LIABILITY' and str(line.account_id)==str(allocation['liability_account_id'])]
    debits=[line for line in lines if line.debit_amount==source.deposit_paid and line.credit_amount==0 and line.account.type=='ASSET']
    if len(credits)!=1 or len(debits)!=1 or any(line.currency!='COP' or line.tenant_id!=company.pk or line.account.tenant_id!=company.pk or line.account.chart_of_accounts.tenant_id!=company.pk or not line.account.is_active for line in lines):
        raise ValidationError('Importe, moneda o cuentas del recibo de anticipo incompatibles.')
    result={'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'liability_account_id':str(credits[0].account_id),'amount':format(source.deposit_paid,'.2f'),'evidence_digest':evidence(allocation['evidence_digest']),'reservation_id':str(source.pk),'customer_id':str(source.customer_id),'independently_verified':False}
    claim=OutboxEvent.objects.filter(pk=advance_claim_id(journal.pk)).first()
    if claim is None:
        if AccountingEventReceipt.objects.filter(tenant=company,event_id=key(source)).exists():raise ValidationError('Falta evidencia de aplicación del anticipo; requiere conciliación.')
        balance=LedgerEntry.plain_objects.filter(tenant=company,account_id=credits[0].account_id,journal_entry__is_posted=True).aggregate(debit=Sum('debit_amount'),credit=Sum('credit_amount'))
        with localcontext() as ctx:
            ctx.prec=38
            available=(balance['credit'] or Decimal(0))-(balance['debit'] or Decimal(0))
        if available<source.deposit_paid:raise ValidationError('El pasivo de anticipos no tiene saldo suficiente.')
    if claim and (claim.event_type!=ADVANCE_APPLIED or claim.payload.get('allocation')!=result):raise ValidationError('Este recibo ya está asignado a otro reconocimiento.')
    return result

@transaction.atomic
def review_recognition(*,actor,provider_id,reservation_id,fiscal_review_id,entry_date,account_mapping,service_evidence_digest,policy_evidence_digest,economic_fact,confirmed,expected_revision,advance_allocation=None):
    if confirmed is not True or economic_fact!='SERVICE_DELIVERED' or type(expected_revision) is not int or expected_revision<0:
        raise ValidationError('Declara expresamente el servicio prestado y confirma su revisión.')
    day=date.fromisoformat(entry_date)
    if day.isoformat()!=entry_date or day>timezone.localdate():raise ValidationError('Fecha económica inválida o futura.')
    user,company,source,fingerprint=locked_source(actor,provider_id,reservation_id)
    if company.currency!='COP':raise ValidationError('Este flujo solo admite COP; no se aplica una tasa implícita.')
    if source.end_date>timezone.now() or day<timezone.localtime(source.end_date).date():
        raise ValidationError('No se reconoce como prestado un servicio cuyo plazo aún no terminó.')
    if AccountingEventReceipt.objects.filter(tenant=company,event_id=key(source)).exists():raise ValidationError('Ya se contabilizó esta reserva; usa la revisión o contrapartida del asiento existente.')
    fiscal=latest_review(company,source)
    if fiscal is None or str(fiscal.pk)!=str(UUID(str(fiscal_review_id))):raise ValidationError('Revisión fiscal no vigente.')
    _,intent=validated_review(fiscal,company,source,fingerprint,recognition_date=entry_date);totals=intent['payload']['totals']
    advance=validated_advance(company,source,advance_allocation,day)
    resolved=accounts(company,account_mapping,totals['tax'])
    if advance and advance['liability_account_id'] in {str(a.pk) for a in resolved.values()}:raise ValidationError('El pasivo de anticipo debe ser distinto de las cuentas de reconocimiento.')
    periods=list(FiscalPeriod.plain_objects.select_for_update().filter(tenant=company,status='open',period_start__lte=day,period_end__gte=day)[:2])
    if len(periods)!=1:raise ValidationError('Se requiere un único periodo abierto para la fecha.')
    old=latest(company,source);previous=old.payload['revision'] if old else 0
    if previous!=expected_revision:raise ValidationError('La revisión contable cambió; recarga.')
    with localcontext() as ctx:
        ctx.prec=38
        receivable_amount=format(source.total_price-source.deposit_paid,'.2f')
    payload={'company_id':str(company.pk),'reservation_id':str(source.pk),'revision':previous+1,
        'reviewed_by':str(user.pk),'source_fingerprint':fingerprint,'fiscal_review_id':str(fiscal.pk),
        'intent_digest':intent['payload_digest'],'totals':totals,'entry_date':entry_date,'period_id':str(periods[0].pk),
        'account_mapping':{role:str(row.pk) for role,row in resolved.items()},
        'service_evidence_digest':evidence(service_evidence_digest),'policy_evidence_digest':evidence(policy_evidence_digest),
        'advance_allocation':advance,'receivable_amount':receivable_amount,
        'economic_fact':'SERVICE_DELIVERED_OWNER_ATTESTED','independently_verified':False}
    row=OutboxEvent.objects.create(id=uuid5(NAMESPACE,':'.join([str(company.pk),str(source.pk),str(previous+1)])),event_type=REVIEW,domain='accounting',aggregate_root=str(source.pk),payload={'review':payload,'review_digest':digest(payload),'company_id':str(company.pk),'revision':previous+1},version=1)
    return {'review_id':str(row.pk),'revision':previous+1,'review_digest':digest(payload),'preview':payload,'ledger_written':False}

@transaction.atomic
def post_recognition(*,actor,provider_id,reservation_id,review_id,confirmed):
    if confirmed is not True:raise ValidationError('Se requiere segunda confirmación para contabilizar.')
    user,company,source,fingerprint=locked_source(actor,provider_id,reservation_id)
    row=latest(company,source)
    if row is None or str(row.pk)!=str(UUID(str(review_id))):raise ValidationError('Revisión contable no vigente.')
    p=row.payload['review']
    if digest(p)!=row.payload.get('review_digest') or p['source_fingerprint']!=fingerprint or p['reviewed_by']!=str(user.pk):raise ValidationError('La fuente o revisión cambió.')
    fiscal=latest_review(company,source)
    if fiscal is None or str(fiscal.pk)!=p['fiscal_review_id']:raise ValidationError('Cambió la revisión fiscal.')
    _,intent=validated_review(fiscal,company,source,fingerprint,recognition_date=p['entry_date'])
    if intent['payload_digest']!=p['intent_digest'] or intent['payload']['totals']!=p['totals']:raise ValidationError('Importes incompatibles.')
    mapping={**p['account_mapping']};mapping.setdefault('tax_liability',None)
    resolved=accounts(company,mapping,p['totals']['tax'])
    day=date.fromisoformat(p['entry_date'])
    if company.currency!='COP' or source.end_date>timezone.now() or day<timezone.localtime(source.end_date).date():raise ValidationError('Hecho económico incompatible.')
    saved_advance=p.get('advance_allocation')
    supplied={k:saved_advance[k] for k in ('journal_id','liability_account_id','evidence_digest')} if saved_advance else None
    advance=validated_advance(company,source,supplied,day)
    if advance!=saved_advance:raise ValidationError('Cambió el anticipo revisado.')
    with localcontext() as ctx:
        ctx.prec=38
        receivable=format(Decimal(p['totals']['gross'])-source.deposit_paid,'.2f')
    if receivable!=p.get('receivable_amount',p['totals']['gross']):raise ValidationError('Cambió el saldo por cobrar.')
    lines=[]
    if Decimal(receivable)>0:lines.append({'account':resolved['receivable'],'debit':receivable})
    lines.append({'account':resolved['revenue'],'credit':p['totals']['net']})
    if advance:
        liability=Account.plain_objects.get(pk=advance['liability_account_id'],tenant=company)
        if liability.pk in {a.pk for a in resolved.values()}:raise ValidationError('Cuenta de anticipo incompatible.')
        lines.append({'account':liability,'debit':advance['amount']})
    if p['totals']['tax']!='0.00':lines.append({'account':resolved['tax_liability'],'credit':p['totals']['tax']})
    replay=AccountingEventReceipt.objects.filter(tenant=company,event_id=key(source)).exists()
    journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=day,description='Servicio prestado reserva '+str(source.pk),lines_data=lines,actor=user,idempotency_key=key(source),period_id=p['period_id'])
    if advance:
        claim_id=advance_claim_id(advance['journal_id'])
        claim_payload={'company_id':str(company.pk),'allocation':advance,'recognition_journal_id':str(journal.pk)}
        claim=OutboxEvent.objects.filter(pk=claim_id).first()
        if claim and claim.payload!=claim_payload:raise ValidationError('Conflicto de aplicación de anticipo.')
        if not claim:OutboxEvent.objects.create(id=claim_id,event_type=ADVANCE_APPLIED,domain='accounting',aggregate_root=str(source.pk),payload=claim_payload,version=1)
    posted_id=uuid5(NAMESPACE,'posted:'+str(source.pk))
    proof={'company_id':str(company.pk),'reservation_id':str(source.pk),'review_id':str(row.pk),'review_digest':row.payload['review_digest'],'journal_id':str(journal.pk),'journal_hash':journal.system_hash}
    existing=OutboxEvent.objects.filter(pk=posted_id).first()
    if existing and (existing.event_type!=POSTED or existing.payload!=proof):raise ValidationError('Conflicto de evidencia de contabilización.')
    if replay and existing is None:raise ValidationError('Falta evidencia de origen del asiento; requiere conciliación.')
    if not existing:OutboxEvent.objects.create(id=posted_id,event_type=POSTED,domain='accounting',aggregate_root=str(source.pk),payload=proof,version=1)
    return {'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'replayed':replay,'ledger_written':True,
        'reversed':JournalEntry.plain_objects.filter(tenant=company,reversed_entry_id=journal.pk,is_posted=True).exists(),
        'fiscal_accepted':False,'money_transferred':False,'independently_verified':False}


REVERSE_REVIEW='accounting.reservation.reversal-reviewed.v1'
REVERSED='accounting.reservation.reversed.v1'

def original_posting(company,source):
    proof=OutboxEvent.objects.filter(pk=uuid5(NAMESPACE,'posted:'+str(source.pk)),event_type=POSTED,aggregate_root=str(source.pk),payload__company_id=str(company.pk)).first()
    if proof is None:raise ValidationError('No hay reconocimiento de esta reserva.')
    journal=JournalEntry.plain_objects.select_for_update().filter(pk=proof.payload['journal_id'],tenant=company,is_posted=True,is_reversal=False).first()
    if journal is None or journal.compute_hash()!=journal.system_hash or journal.system_hash!=proof.payload['journal_hash']:
        raise ValidationError('El asiento de origen requiere conciliación.')
    return journal

@transaction.atomic
def review_reversal(*,actor,provider_id,reservation_id,reason,evidence_digest,confirmed):
    if confirmed is not True or not isinstance(reason,str) or not 10<=len(reason.strip())<=500:
        raise ValidationError('Confirma un motivo de contrapartida entre 10 y 500 caracteres.')
    user,company,source,_=locked_source(actor,provider_id,reservation_id,allowed_statuses=('PENDING','CONFIRMED','CANCELLED','COMPLETED'))
    journal=original_posting(company,source)
    payload={'company_id':str(company.pk),'reservation_id':str(source.pk),'journal_id':str(journal.pk),
        'journal_hash':journal.system_hash,'reviewed_by':str(user.pk),'reason':reason.strip(),'evidence_digest':evidence(evidence_digest)}
    identifier=uuid5(NAMESPACE,'reverse-review:'+str(source.pk))
    existing=OutboxEvent.objects.filter(pk=identifier).first()
    if existing:
        if existing.event_type!=REVERSE_REVIEW or existing.payload!=payload:raise ValidationError('Existe otra revisión de contrapartida; requiere conciliación.')
    else:OutboxEvent.objects.create(id=identifier,event_type=REVERSE_REVIEW,domain='accounting',aggregate_root=str(source.pk),payload=payload,version=1)
    return {'review_id':str(identifier),'original_journal_id':str(journal.pk),'ledger_written':False}

@transaction.atomic
def reverse_recognition(*,actor,provider_id,reservation_id,review_id,confirmed):
    if confirmed is not True:raise ValidationError('Se requiere segunda confirmación para la contrapartida.')
    user,company,source,_=locked_source(actor,provider_id,reservation_id,allowed_statuses=('PENDING','CONFIRMED','CANCELLED','COMPLETED'))
    journal=original_posting(company,source)
    identifier=uuid5(NAMESPACE,'reverse-review:'+str(source.pk))
    if str(identifier)!=str(UUID(str(review_id))):raise ValidationError('Revisión de contrapartida inválida.')
    review=OutboxEvent.objects.filter(pk=identifier,event_type=REVERSE_REVIEW,payload__company_id=str(company.pk)).first()
    if review is None or review.payload.get('reviewed_by')!=str(user.pk) or review.payload.get('journal_hash')!=journal.system_hash:
        raise ValidationError('Revisión de contrapartida no vigente.')
    posted_id=uuid5(NAMESPACE,'reversed:'+str(source.pk));existing=OutboxEvent.objects.filter(pk=posted_id).first()
    if existing:
        reverse=JournalEntry.plain_objects.filter(pk=existing.payload.get('journal_id'),tenant=company,reversed_entry_id=journal.pk,is_posted=True).first()
        if existing.event_type!=REVERSED or reverse is None or reverse.compute_hash()!=reverse.system_hash or existing.payload.get('journal_hash')!=reverse.system_hash or existing.payload.get('review_digest')!=digest(review.payload):
            raise ValidationError('Evidencia de contrapartida incompatible.')
        return {'journal_id':str(reverse.pk),'original_journal_id':str(journal.pk),'replayed':True,'ledger_written':True,'money_transferred':False}
    reverse=LedgerEngine.reverse_entry(journal.pk,review.payload['reason'],tenant_id=company.pk,actor=user)
    OutboxEvent.objects.create(id=posted_id,event_type=REVERSED,domain='accounting',aggregate_root=str(source.pk),payload={
        'company_id':str(company.pk),'journal_id':str(reverse.pk),'journal_hash':reverse.system_hash,'original_journal_id':str(journal.pk),
        'review_id':str(review.pk),'review_digest':digest(review.payload)},version=1)
    return {'journal_id':str(reverse.pk),'original_journal_id':str(journal.pk),'replayed':False,'ledger_written':True,'money_transferred':False}

@transaction.atomic
def recognition_status(*,actor,provider_id,reservation_id,before_revision=None):
    """Recover persisted result without re-authorizing or reconstructing history."""
    user,company,source,fingerprint=locked_source(actor,provider_id,reservation_id,allowed_statuses=('PENDING','CONFIRMED','CANCELLED','COMPLETED'))
    current=latest(company,source)
    review=None
    if current:
        body=current.payload.get('review')
        if not isinstance(body,dict) or digest(body)!=current.payload.get('review_digest') or body.get('company_id')!=str(company.pk) or body.get('reservation_id')!=str(source.pk):raise ValidationError('La revisión requiere conciliación.')
        allocation=body.get('advance_allocation') or {}
        advance_matches=Decimal(allocation.get('amount','0.00'))==source.deposit_paid
        fiscal=latest_review(company,source)
        fiscal_matches=fiscal is not None and str(fiscal.pk)==body.get('fiscal_review_id')
        review={'review_id':str(current.pk),'revision':body['revision'],'review_digest':current.payload['review_digest'],'preview':body,'ledger_written':False,'source_matches':body.get('source_fingerprint')==fingerprint and advance_matches and fiscal_matches,'reviewed_by_current_owner':body.get('reviewed_by')==str(user.pk)}
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=key(source)).first()
    proof=OutboxEvent.objects.filter(pk=uuid5(NAMESPACE,'posted:'+str(source.pk))).first()
    posting=None
    if receipt or proof:
        journal=original_posting(company,source)
        if receipt is None or receipt.journal_id!=journal.pk or proof.payload.get('review_id')!=(review or {}).get('review_id') or proof.payload.get('review_digest')!=(review or {}).get('review_digest'):raise ValidationError('La evidencia de resultado requiere conciliación.')
        reversals=list(JournalEntry.plain_objects.filter(tenant=company,reversed_entry_id=journal.pk,is_posted=True)[:2])
        if len(reversals)>1 or any(r.compute_hash()!=r.system_hash for r in reversals):raise ValidationError('Contrapartida incompatible.')
        posting={'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'reversed':bool(reversals),'reversal_journal_id':str(reversals[0].pk) if reversals else None}
    history_query=OutboxEvent.objects.filter(event_type=REVIEW,aggregate_root=str(source.pk),payload__company_id=str(company.pk)).order_by('-payload__revision')
    if before_revision is not None:
        if not isinstance(before_revision,str) or not re.fullmatch('[1-9][0-9]{0,9}',before_revision):raise ValidationError('Cursor de historial inválido.')
        history_query=history_query.filter(payload__revision__lt=int(before_revision))
    rows=list(history_query[:21]);history=[]
    for row in rows[:20]:
        p=row.payload.get('review')
        if not isinstance(p,dict) or digest(p)!=row.payload.get('review_digest'):raise ValidationError('Historial inconsistente.')
        history.append({'review_id':str(row.pk),'revision':p['revision'],'entry_date':p['entry_date'],'totals':p['totals'],'review_digest':row.payload['review_digest']})
    return {'company_id':str(company.pk),'reservation_id':str(source.pk),'source_status':source.status,'read_only':True,'ledger_written':False,'review':review,'posting':posting,'history':history,'next_before_revision':str(rows[19].payload['revision']) if len(rows)>20 else None,'confirmations_restored':False}
