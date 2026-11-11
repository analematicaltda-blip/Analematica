"""Company-owned cancellation charges, separate from tax withholding.
Versioned contract conditions and reviewed settlement proposals; no money execution.
"""
from uuid import UUID,uuid5
from datetime import date,datetime,timedelta
from decimal import Decimal,ROUND_HALF_UP,localcontext
from django.db import transaction
from django.utils import timezone
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import _money,_format_money
from apps.core_erp.accounting.commercial_tax_posting import identifier,digest
from ..gestion_contable.compras.native_purchase import context,positive
from ..gestion_operativa.modulos_genericos.reservas.models import PoliticaCancelacion
from apps.domain_business.operativa.models import Reservation
NS=UUID('5ed51cbd-920a-4908-991a-8684b4147da3')
REVIEW='commercial.cancellation-policy.reviewed.v1'
PUBLISHED='commercial.cancellation-policy.published.v1'
BOUND='commercial.cancellation-policy.acceptance-declared.v1'
CASE_REVIEW='commercial.cancellation-charge.reviewed.v1'
CASE_RECORDED='commercial.cancellation-charge.proposed.v1'
SCOPES={'COMPRA','PLAN_TURISTICO','SERVICIO'}
BASES={'REQUESTED_REFUND','CONTRACT_TOTAL'}
REASONS={'STANDARD_CANCELLATION','STATUTORY_EXCEPTION','SUPPLIER_FAILURE','COMPANY_WAIVER'}

def key(kind,company,value):return uuid5(NS,kind+':'+str(company.pk)+':'+str(value))
def event_key(kind,b):
    if kind in {REVIEW,CASE_REVIEW}:return b['request_id']
    if kind==PUBLISHED:return str(b['policy_id'])+':'+str(b['revision'])
    return b['reservation_id']
def write(kind,company,provider,b):
    return OutboxEvent.objects.create(id=key(kind,company,event_key(kind,b)),event_type=kind,domain='commercial',aggregate_root=str(company.pk),version=1,payload={'company_id':str(company.pk),'provider_id':str(provider.pk),'body':b,'digest':fingerprint(b)})
def read(row,kind,company,provider):
    if row is None or row.event_type!=kind or row.domain!='commercial' or row.version!=1 or row.aggregate_root!=str(company.pk) or set(row.payload)!={'company_id','provider_id','body','digest'} or row.payload['company_id']!=str(company.pk) or row.payload['provider_id']!=str(provider.pk):raise AccountingError('Scoped cancellation evidence unavailable.')
    b=row.payload['body']
    if not isinstance(b,dict) or fingerprint(b)!=row.payload['digest'] or row.pk!=key(kind,company,event_key(kind,b)):raise AccountingError('Cancellation evidence changed.')
    return b

def text(v,maximum):
    if not isinstance(v,str) or v!=v.strip() or not 1<=len(v)<=maximum or any(ord(c)<32 and c not in '\n\r\t' for c in v):raise AccountingError('Explicit plain text terms required.')
    return v

def config(values):
    import re
    if not isinstance(values,dict) or set(values) not in ({'name','terms','scope','percentage','basis','active','valid_from','valid_until'},{'name','terms','scope','percentage','basis','active','valid_from','valid_until','timing_tiers'}):raise AccountingError('Explicit commercial charge policy required.')
    p=values['percentage']
    if not isinstance(p,str) or not re.fullmatch(r'(0|[1-9][0-9]{0,2})(\.[0-9]{1,2})?',p) or Decimal(p)>100 or values['scope'] not in SCOPES or values['basis'] not in BASES or type(values['active']) is not bool:raise AccountingError('Percentage0..100 with at most2 decimals and explicit scope/base required.')
    tiers=values.get('timing_tiers')
    if 'timing_tiers' in values:
        if not isinstance(tiers,list) or not 1<=len(tiers)<=10:raise AccountingError('One to ten explicit cancellation time bands required.')
        previous_day=3651;previous_rate=Decimal('-1')
        for tier in tiers:
            if not isinstance(tier,dict) or set(tier)!={'min_days_before','percentage'} or type(tier['min_days_before']) is not int or not 0<=tier['min_days_before']<previous_day:raise AccountingError('Descending distinct day thresholds0..3650 required.')
            rate=tier['percentage']
            if not isinstance(rate,str) or not re.fullmatch(r'(0|[1-9][0-9]{0,2})(\.[0-9]{1,2})?',rate) or not previous_rate<=Decimal(rate)<=100:raise AccountingError('Rates must increase or stay equal as service approaches.')
            previous_day=tier['min_days_before'];previous_rate=Decimal(rate)
        if tiers[-1]['min_days_before']!=0 or Decimal(p)!=Decimal(tiers[-1]['percentage']):raise AccountingError('Final band must cover day zero; no uncovered intervals.')
        tiers=[{**t,'percentage':format(Decimal(t['percentage']),'.2f')} for t in tiers]
    start,end=date.fromisoformat(values['valid_from']),date.fromisoformat(values['valid_until'])
    if start.isoformat()!=values['valid_from'] or end.isoformat()!=values['valid_until'] or end<start:raise AccountingError('Canonical offer validity interval required.')
    return {**values,'name':text(values['name'],100),'terms':text(values['terms'],2000),'percentage':format(Decimal(p),'.2f'),**({'timing_tiers':tiers} if tiers is not None else {})}

def policy(provider,policy_id):
    row=PoliticaCancelacion.objects.select_for_update().filter(pk=positive(policy_id),perfil_ref_id=provider.pk).first()
    if row is None:raise AccountingError('Policy unavailable in this company.')
    return row

def latest(company,policy_id):return OutboxEvent.objects.filter(event_type=PUBLISHED,payload__company_id=str(company.pk),payload__body__policy_id=policy_id).order_by('-payload__body__revision').first()

def version(company,provider,policy_id,revision):
    row=OutboxEvent.objects.filter(pk=key(PUBLISHED,company,str(policy_id)+':'+str(revision))).first();b=read(row,PUBLISHED,company,provider);r=read(OutboxEvent.objects.filter(pk=b['review_id']).first(),REVIEW,company,provider)
    if b['policy_id']!=policy_id or b['revision']!=revision or b['config']!=config(b['config']) or b['review_digest']!=fingerprint(r) or r['config']!=b['config'] or r['expected_revision']!=revision-1 or r['policy_id'] not in {None,policy_id}:raise AccountingError('Published cancellation policy changed.')
    return row,b

def current(company,provider,row):
    last=latest(company,row.pk)
    if last is None:return None
    _,b=version(company,provider,row.pk,last.payload['body']['revision'])
    if row.nombre!=b['config']['name'] or row.descripcion!=b['config']['terms']:raise AccountingError('Policy text changed outside versioned control.')
    return b

def flags(company,provider):return {'company_id':str(company.pk),'provider_id':str(provider.pk),'currency':'COP','ledger_written':False,'money_transferred':False,'reservation_cancelled':False,'tax_withholding':False,'legal_applicability_verified':False,'funds_verified':False}

@transaction.atomic
def review_policy(*,actor,provider_id,request_id,policy_id,expected_revision,values,confirmed):
    user,provider,company=context(actor,provider_id);identifier(request_id);c=config(values)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:raise AccountingError('First confirmation and policy revision required.')
    row=policy(provider,policy_id) if policy_id is not None else None;b=current(company,provider,row) if row else None;revision=b['revision'] if b else 0
    content={'request_id':request_id,'policy_id':policy_id,'expected_revision':expected_revision,'config':c,'reviewed_by':str(user.pk)}
    old=OutboxEvent.objects.filter(pk=key(REVIEW,company,request_id)).first()
    if old:
        saved=read(old,REVIEW,company,provider)
        if {k:v for k,v in saved.items() if k!='expires_at'}!=content:raise AccountingError('Policy request identity already used.')
        return {**flags(company,provider),'review_id':str(old.pk),'preview':saved}
    if expected_revision!=revision or revision>=100:raise AccountingError('Policy revision changed or history limit reached.')
    content['expires_at']=(timezone.now()+timedelta(minutes=15)).isoformat();saved=write(REVIEW,company,provider,content)
    return {**flags(company,provider),'review_id':str(saved.pk),'preview':content}

@transaction.atomic
def publish_policy(*,actor,provider_id,review_id,confirmed):
    user,provider,company=context(actor,provider_id);identifier(review_id);r=read(OutboxEvent.objects.filter(pk=review_id).first(),REVIEW,company,provider)
    if confirmed is not True or r['reviewed_by']!=str(user.pk):raise AccountingError('Second confirmation by same administrator required.')
    existing=list(OutboxEvent.objects.filter(event_type=PUBLISHED,payload__company_id=str(company.pk),payload__body__review_id=review_id)[:2])
    if existing:
        if len(existing)!=1:raise AccountingError('Duplicate policy publication evidence.')
        p=read(existing[0],PUBLISHED,company,provider);version(company,provider,p['policy_id'],p['revision']);current(company,provider,policy(provider,p['policy_id']))
        return {**flags(company,provider),**p,'replayed':True}
    row=policy(provider,r['policy_id']) if r['policy_id'] is not None else None;last=current(company,provider,row) if row else None
    if (last['revision'] if last else 0)!=r['expected_revision'] or timezone.now()>=datetime.fromisoformat(r['expires_at']):raise AccountingError('Policy changed or review expired.')
    c=r['config']
    if row is None:row=PoliticaCancelacion.objects.create(perfil_ref_id=provider.pk,nombre=c['name'],descripcion=c['terms'])
    else:row.nombre=c['name'];row.descripcion=c['terms'];row.save(update_fields=['nombre','descripcion'])
    b={'policy_id':row.pk,'revision':r['expected_revision']+1,'config':c,'review_id':review_id,'review_digest':fingerprint(r)};write(PUBLISHED,company,provider,b)
    return {**flags(company,provider),**b,'replayed':False}

@transaction.atomic
def policy_state(*,actor,provider_id,policy_id):
    _,provider,company=context(actor,provider_id);row=policy(provider,policy_id);b=current(company,provider,row)
    return {**flags(company,provider),'policy_id':row.pk,'revision':b['revision'] if b else 0,'config':b['config'] if b else None,'legacy_name':row.nombre,'legacy_terms':row.descripcion,'read_only':True,'confirmations_restored':False}

def reservation(company,reservation_id):
    identifier(reservation_id);r=Reservation.plain_objects.select_for_update().filter(pk=reservation_id,tenant=company).first()
    if r is None:raise AccountingError('Reservation unavailable in company.')
    return r

def snapshot(r):return {'reservation_id':str(r.pk),'customer_id':str(r.customer_id),'total':format(r.total_price,'.2f'),'start':r.start_date.isoformat(),'end':r.end_date.isoformat(),'content_type':r.content_type_id,'object_id':str(r.object_id)}

@transaction.atomic
def bind_policy(*,actor,provider_id,reservation_id,policy_id,policy_revision,accepted_at,consent_kind,consent_digest,confirmed):
    user,provider,company=context(actor,provider_id);r=reservation(company,reservation_id);row=policy(provider,policy_id);head=current(company,provider,row);digest(consent_digest)
    if confirmed is not True or consent_kind not in {'NEW_CONTRACT','ACCEPTED_AMENDMENT'} or type(policy_revision) is not int or r.status not in {'PENDING','CONFIRMED'}:raise AccountingError('Explicit customer acceptance declaration and open reservation required.')
    published,b=version(company,provider,policy_id,policy_revision);accepted=datetime.fromisoformat(accepted_at)
    if accepted.tzinfo is None or accepted.utcoffset().total_seconds()!=0 or accepted>timezone.now() or accepted<published.created_at or not b['config']['valid_from']<=timezone.localdate(accepted).isoformat()<=b['config']['valid_until']:raise AccountingError('Acceptance must follow publication and match offer validity.')
    content={'reservation_id':reservation_id,'policy_id':policy_id,'policy_revision':policy_revision,'policy_digest':fingerprint(b),'reservation_snapshot_digest':fingerprint(snapshot(r)),'accepted_at':accepted_at,'consent_kind':consent_kind,'consent_digest':consent_digest,'declared_by':str(user.pk)}
    old=OutboxEvent.objects.filter(pk=key(BOUND,company,reservation_id)).first()
    if old:
        if read(old,BOUND,company,provider)!=content:raise AccountingError('Contract policy is immutable; later percentages cannot replace accepted conditions.')
        return {**flags(company,provider),'binding':content,'replayed':True}
    if head is None or head['revision']!=policy_revision or not b['config']['active']:raise AccountingError('Select current active policy for new acceptance.')
    if consent_kind=='NEW_CONTRACT' and published.created_at>r.created_at:raise AccountingError('Existing booking requires declared accepted amendment; no retroactive policy.')
    if OutboxEvent.objects.filter(event_type=CASE_RECORDED,payload__company_id=str(company.pk),payload__body__reservation_id=reservation_id).exists():raise AccountingError('Settlement proposal already registered.')
    write(BOUND,company,provider,content)
    return {**flags(company,provider),'binding':content,'replayed':False}

def binding(company,provider,r):
    b=read(OutboxEvent.objects.filter(pk=key(BOUND,company,str(r.pk))).first(),BOUND,company,provider);_,p=version(company,provider,b['policy_id'],b['policy_revision']);current(company,provider,policy(provider,b['policy_id']))
    if fingerprint(p)!=b['policy_digest'] or fingerprint(snapshot(r))!=b['reservation_snapshot_digest']:raise AccountingError('Accepted source changed; reconcile contract instead of replacing it.')
    return b,p

def calculation(r,c,requested_refund,reason,cancellation_at=None):
    requested=_money(requested_refund);total=_money(format(r.total_price,'.2f'))
    if requested<=0 or requested>total or reason not in REASONS:raise AccountingError('Positive declared refund within contract and explicit applicability reason required.')
    percentage=c['percentage'];timing={}
    if 'timing_tiers' in c:
        from zoneinfo import ZoneInfo
        if not isinstance(cancellation_at,str):raise AccountingError('Explicit actual cancellation timestamp required for time bands.')
        at=datetime.fromisoformat(cancellation_at.replace('Z','+00:00'))
        if at.tzinfo is None or at.utcoffset().total_seconds()!=0 or at>timezone.now():raise AccountingError('Cancellation must use nonfuture UTC timestamp.')
        service_day=r.start_date.astimezone(ZoneInfo('America/Bogota')).date() if isinstance(r.start_date,datetime) and r.start_date.tzinfo else r.start_date.date() if isinstance(r.start_date,datetime) else r.start_date
        days=(service_day-at.astimezone(ZoneInfo('America/Bogota')).date()).days
        if days<0:raise AccountingError('Post-service cancellation requires a separate reviewed claim.')
        tier=next(t for t in c['timing_tiers'] if days>=t['min_days_before']);percentage=tier['percentage'];timing={'cancellation_at':cancellation_at,'service_day':service_day.isoformat(),'days_before_service':days,'tier_min_days_before':tier['min_days_before'],'calendar_zone':'America/Bogota'}
    base=requested if c['basis']=='REQUESTED_REFUND' else total
    with localcontext() as ctx:
        ctx.prec=38;raw=int((Decimal(base)*Decimal(percentage)/100).quantize(Decimal(1),rounding=ROUND_HALF_UP))
    fee=0 if reason!='STANDARD_CANCELLATION' else min(raw,requested)
    return {'contract_total':_format_money(total),'refund_requested':_format_money(requested),'fee_base':_format_money(base),'percentage':percentage,**timing,'fee_amount':_format_money(fee),'refund_net':_format_money(requested-fee),'capped':reason=='STANDARD_CANCELLATION' and raw>requested,'waived':reason!='STANDARD_CANCELLATION','reason_code':reason,'scope':c['scope'],'basis':c['basis']}

def case_head(company,reservation_id):return OutboxEvent.objects.filter(event_type=CASE_REVIEW,payload__company_id=str(company.pk),payload__body__reservation_id=reservation_id).order_by('-payload__body__revision').first()

@transaction.atomic
def review_case(*,actor,provider_id,reservation_id,request_id,requested_refund,reason_code,evidence_digest,expected_revision,confirmed,cancellation_at=None):
    user,provider,company=context(actor,provider_id);r=reservation(company,reservation_id);b,p=binding(company,provider,r);identifier(request_id);digest(evidence_digest)
    if confirmed is not True or type(expected_revision) is not int or r.status not in {'PENDING','CONFIRMED'}:raise AccountingError('First contract/applicability review required before cancellation.')
    calc=calculation(r,p['config'],requested_refund,reason_code,cancellation_at)
    if 'timing_tiers' in p['config'] and datetime.fromisoformat(cancellation_at.replace('Z','+00:00'))<datetime.fromisoformat(b['accepted_at']):raise AccountingError('Cancellation cannot precede accepted conditions.')
    old=OutboxEvent.objects.filter(pk=key(CASE_REVIEW,company,request_id)).first();head=case_head(company,reservation_id);revision=read(head,CASE_REVIEW,company,provider)['revision'] if head else 0
    content={'reservation_id':reservation_id,'request_id':request_id,'revision':expected_revision+1,'binding_digest':fingerprint(b),'policy_id':b['policy_id'],'policy_revision':b['policy_revision'],'calculation':calc,'evidence_digest':evidence_digest,'reviewed_by':str(user.pk)}
    if old:
        saved=read(old,CASE_REVIEW,company,provider)
        if {k:v for k,v in saved.items() if k!='expires_at'}!=content:raise AccountingError('Settlement request identity changed.')
        return {**flags(company,provider),'review_id':str(old.pk),'preview':saved,'proposal_only':True}
    if revision!=expected_revision or revision>=100 or OutboxEvent.objects.filter(pk=key(CASE_RECORDED,company,reservation_id)).exists():raise AccountingError('Proposal already registered or revision changed.')
    content['expires_at']=(timezone.now()+timedelta(minutes=15)).isoformat();saved=write(CASE_REVIEW,company,provider,content)
    return {**flags(company,provider),'review_id':str(saved.pk),'preview':content,'proposal_only':True}

@transaction.atomic
def confirm_case(*,actor,provider_id,reservation_id,review_id,confirmed):
    user,provider,company=context(actor,provider_id);r=reservation(company,reservation_id);identifier(review_id);review=case_head(company,reservation_id);b=read(review,CASE_REVIEW,company,provider)
    if confirmed is not True or str(review.pk)!=review_id or b['reviewed_by']!=str(user.pk):raise AccountingError('Second confirmation of current proposal by same administrator required.')
    old=OutboxEvent.objects.filter(pk=key(CASE_RECORDED,company,reservation_id)).first()
    if old:
        saved=read(old,CASE_RECORDED,company,provider)
        if saved['review_id']!=review_id or saved['review_digest']!=fingerprint(b):raise AccountingError('Different settlement already registered.')
        return {**flags(company,provider),**saved,'proposal_only':True,'replayed':True}
    accepted,p=binding(company,provider,r)
    if r.status not in {'PENDING','CONFIRMED'} or fingerprint(accepted)!=b['binding_digest'] or calculation(r,p['config'],b['calculation']['refund_requested'],b['calculation']['reason_code'],b['calculation'].get('cancellation_at'))!=b['calculation'] or timezone.now()>=datetime.fromisoformat(b['expires_at']):raise AccountingError('Contract changed or proposal review expired.')
    saved={'reservation_id':reservation_id,'review_id':review_id,'review_digest':fingerprint(b),'policy_id':b['policy_id'],'policy_revision':b['policy_revision'],'calculation':b['calculation']};write(CASE_RECORDED,company,provider,saved)
    return {**flags(company,provider),**saved,'proposal_only':True,'replayed':False}

@transaction.atomic
def case_state(*,actor,provider_id,reservation_id):
    _,provider,company=context(actor,provider_id);r=reservation(company,reservation_id);bound=OutboxEvent.objects.filter(pk=key(BOUND,company,reservation_id)).first();b,p=binding(company,provider,r) if bound else (None,None);head=case_head(company,reservation_id);review=read(head,CASE_REVIEW,company,provider) if head else None;row=OutboxEvent.objects.filter(pk=key(CASE_RECORDED,company,reservation_id)).first();saved=read(row,CASE_RECORDED,company,provider) if row else None
    if saved and (review is None or saved['review_id']!=str(head.pk) or saved['review_digest']!=fingerprint(review) or saved['calculation']!=review['calculation']):raise AccountingError('Settlement origin changed.')
    return {**flags(company,provider),'reservation_id':reservation_id,'binding':b,'config':p['config'] if p else None,'revision':review['revision'] if review else 0,'review':review,'registered':saved,'read_only':True,'confirmations_restored':False,'proposal_only':True}

@transaction.atomic
def sources(*,actor,provider_id,policy_after,reservation_after):
    _,provider,company=context(actor,provider_id);policies=PoliticaCancelacion.objects.filter(perfil_ref_id=provider.pk).order_by('pk');reservations=Reservation.plain_objects.filter(tenant=company).order_by('pk')
    if policy_after is not None:policies=policies.filter(pk__gt=positive(policy_after))
    if reservation_after is not None:identifier(reservation_after);reservations=reservations.filter(pk__gt=reservation_after)
    pp=list(policies[:21]);rr=list(reservations[:21]);result=[]
    for row in pp[:20]:
        b=current(company,provider,row);result.append({'policy_id':row.pk,'name':row.nombre,'revision':b['revision'] if b else 0,'config':b['config'] if b else None})
    return {**flags(company,provider),'policies':result,'reservations':[{'reservation_id':str(r.pk),'total':format(r.total_price,'.2f'),'status':r.status,'start_date':r.start_date.isoformat()} for r in rr[:20]],'next_policy_after':pp[19].pk if len(pp)>20 else None,'next_reservation_after':str(rr[19].pk) if len(rr)>20 else None,'read_only':True}

# Financial authorizations are separate from commercial proposal confirmations.
def review_refund(**values):
    from .refund_orders import review_refund as operation
    return operation(**values)
def authorize_refund(**values):
    from .refund_orders import authorize_refund as operation
    return operation(**values)
def refund_state(**values):
    from .refund_orders import refund_state as operation
    return operation(**values)

def prepare_wallet_refund(**values):
    from .wallet_refund import prepare_wallet_refund as operation
    return operation(**values)
def review_wallet_refund(**values):
    from .wallet_refund import review_wallet_refund as operation
    return operation(**values)
def execute_wallet_refund(**values):
    from .wallet_refund import execute_wallet_refund as operation
    return operation(**values)
def wallet_refund_state(**values):
    from .wallet_refund import wallet_refund_state as operation
    return operation(**values)

def wallet_refund_sources(**values):
    from .wallet_refund import wallet_refund_sources as operation
    return operation(**values)

def review_wallet_refund_lifecycle(**values):
    from .wallet_refund_lifecycle import review_wallet_refund_lifecycle as operation
    return operation(**values)
def confirm_wallet_refund_lifecycle(**values):
    from .wallet_refund_lifecycle import confirm_wallet_refund_lifecycle as operation
    return operation(**values)
def wallet_refund_lifecycle_state(**values):
    from .wallet_refund_lifecycle import wallet_refund_lifecycle_state as operation
    return operation(**values)
