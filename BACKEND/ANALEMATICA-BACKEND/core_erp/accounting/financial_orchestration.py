"""Owner-scoped durable financial rehearsal. Never executes money or desktop tasks.

Two separate confirmations and an impact review bind to one immutable intent.
This is not a bank authorization, an authenticated bank destination, or a worker.
"""
from datetime import timedelta
from uuid import UUID, uuid5
import re
from django.db import transaction
from django.utils import timezone
from apps.core_erp.outbox_models import OutboxEvent
from .exceptions import AccountingError
from .integrity import fingerprint
from .validation import lock_company, current_actor, money

NS = UUID('be39af97-2dab-4a04-a13b-7e590a2f69b2')
PREFIX = 'accounting.financial_rehearsal.'
FIELDS = {'schema', 'company_id', 'request_id', 'purpose', 'amount', 'currency',
          'beneficiary_ref', 'source_evidence_digest'}

def identifier(company, request, step):
    return uuid5(NS, str(company)+':'+str(request)+':'+step)

def authority(company_id, actor, provider_id):
    company = lock_company(company_id)
    user = current_actor(actor)
    if getattr(user, 'is_agent', False):
        raise AccountingError('A personal administrator must confirm; agents cannot approve.')
    from apps.turismo.services.company_identity import resolve_company
    if resolve_company(user, provider_id).tenant.pk != company.pk:
        raise AccountingError('Verified owner/company binding required.')
    return company, user

def normalize(intent, company):
    if not isinstance(intent, dict) or set(intent) != FIELDS or intent['schema'] != 'sgacd-financial-rehearsal-v1':
        raise AccountingError('Explicit financial rehearsal contract required.')
    for key in ('company_id', 'request_id', 'beneficiary_ref'):
        if not isinstance(intent[key], str) or str(UUID(intent[key])) != intent[key]:
            raise AccountingError('Canonical scoped identifiers required.')
    if intent['company_id'] != str(company.pk) or intent['currency'] != 'COP' or company.currency != 'COP':
        raise AccountingError('Only explicitly scoped COP rehearsals supported.')
    if intent['purpose'] not in ('SUPPLIER_PAYMENT', 'PAYROLL_BATCH'):
        raise AccountingError('Unsupported purpose.')
    if not isinstance(intent['amount'], str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,11})\.[0-9]{2}', intent['amount']) or money(intent['amount']) <= 0:
        raise AccountingError('Positive bounded exact monetary string required.')
    if not isinstance(intent['source_evidence_digest'], str) or not re.fullmatch('[0-9a-f]{64}', intent['source_evidence_digest']):
        raise AccountingError('Reviewed source evidence digest required.')
    return dict(intent)

def write(company, request, step, body):
    return OutboxEvent.objects.create(id=identifier(company, request, step),
        event_type=PREFIX+step+'.v1', domain='accounting', aggregate_root=request,
        payload=body, version=1)

def read(company, request, step):
    row = OutboxEvent.objects.filter(pk=identifier(company, request, step)).first()
    if row and (row.event_type != PREFIX+step+'.v1' or row.domain != 'accounting'
                or row.aggregate_root != request or row.version != 1):
        raise AccountingError('Persisted rehearsal identity conflicts.')
    return row

def load(company, user, request_id, plan_digest, *, allow_cancelled=False):
    request = str(UUID(str(request_id)))
    row = read(company.pk, request, 'prepared')
    if row is None:
        raise AccountingError('Scoped rehearsal unavailable.')
    body = row.payload
    if (not isinstance(body, dict) or set(body) != {'intent', 'plan_digest', 'actor_id', 'expires_at'}
            or body['actor_id'] != str(user.pk) or not isinstance(body['intent'],dict) or body['intent'].get('request_id') != request
            or normalize(body['intent'], company) != body['intent']
            or fingerprint(body['intent']) != body['plan_digest'] or plan_digest != body['plan_digest']):
        raise AccountingError('Actor or reviewed intent changed.')
    if read(company.pk, request, 'cancelled') and not allow_cancelled:
        raise AccountingError('Rehearsal cancelled; approvals cannot be reused.')
    return request, body

def not_expired(body):
    from django.utils.dateparse import parse_datetime
    end = parse_datetime(body['expires_at'])
    if end is None or timezone.is_naive(end) or timezone.now() >= end:
        raise AccountingError('Rehearsal expired; prepare a new request and review again.')

def approval(company, request, body, step):
    row = read(company.pk, request, step)
    expected = {'company_id': str(company.pk), 'actor_id': body['actor_id'],
                'request_id': request, 'plan_digest': body['plan_digest'], 'step': step}
    if row is None or row.payload != expected:
        raise AccountingError('Separate bound confirmation required.')
    return expected

def result(company, request, digest, status, replayed=False):
    return {'schema': 'sgacd-financial-rehearsal-result-v1', 'company_id': str(company.pk),
            'request_id': request, 'plan_digest': digest, 'status': status, 'replayed': replayed,
            'payment_executed': False, 'bank_destination_verified': False,
            'source_independently_verified': False, 'network_called': False,
            'desktop_job_created': False, 'ledger_written': False,
            'usable_as_payment_authorization': False}

@transaction.atomic
def prepare(company_id, *, actor, provider_id, intent, confirmed=False):
    company, user = authority(company_id, actor, provider_id)
    if confirmed is not True:
        raise AccountingError('Explicit preparation review required.')
    intent = normalize(intent, company); request = intent['request_id']; digest = fingerprint(intent)
    old = read(company.pk, request, 'prepared')
    if old:
        _, body = load(company, user, request, digest)
        not_expired(body)
        if body['intent'] != intent:
            raise AccountingError('Request already bound to another intent.')
        replayed = True
    else:
        body = {'intent': intent, 'plan_digest': digest, 'actor_id': str(user.pk),
                'expires_at': (timezone.now()+timedelta(minutes=5)).isoformat()}
        write(company.pk, request, 'prepared', body); replayed = False
    return {**result(company, request, digest, 'PREPARED', replayed), 'intent': intent,
            'expires_at': body['expires_at']}

@transaction.atomic
def confirm(company_id, *, actor, provider_id, request_id, plan_digest, step, confirmed):
    company, user = authority(company_id, actor, provider_id)
    if confirmed is not True or type(step) is not int or step not in (1, 2):
        raise AccountingError('One explicit confirmation step required.')
    request, body = load(company, user, request_id, plan_digest); not_expired(body)
    if step == 2:
        approval(company, request, body, 'confirmation1')
    name = 'confirmation'+str(step)
    old = read(company.pk, request, name)
    if old:
        approval(company, request, body, name)
    else:
        write(company.pk, request, name, {'company_id': str(company.pk), 'actor_id': str(user.pk),
            'request_id': request, 'plan_digest': body['plan_digest'], 'step': name})
    return result(company, request, plan_digest, 'CONFIRMED_'+str(step), bool(old))

@transaction.atomic
def simulate(company_id, *, actor, provider_id, request_id, plan_digest, impact_confirmation, confirmed=False):
    company, user = authority(company_id, actor, provider_id)
    if confirmed is not True:
        raise AccountingError('Explicit impact review required.')
    request, body = load(company, user, request_id, plan_digest)
    approval(company, request, body, 'confirmation1'); approval(company, request, body, 'confirmation2')
    intent = body['intent']
    phrase = 'SIMULAR '+intent['amount']+' COP A '+intent['beneficiary_ref']
    if impact_confirmation != phrase:
        raise AccountingError('Exact amount and destination impact review required.')
    expected = {'company_id': str(company.pk), 'actor_id': str(user.pk),
                'request_id': request, 'plan_digest': plan_digest, 'status': 'SIMULATED_ONLY'}
    old = read(company.pk, request, 'simulated')
    if old:
        if old.payload != expected:
            raise AccountingError('Stored simulation differs from reviewed intent.')
    else:
        not_expired(body)
        write(company.pk, request, 'simulated', expected)
    return result(company, request, plan_digest, 'SIMULATED_ONLY', bool(old))

@transaction.atomic
def cancel(company_id, *, actor, provider_id, request_id, plan_digest, confirmed):
    company, user = authority(company_id, actor, provider_id)
    if confirmed is not True:
        raise AccountingError('Explicit cancellation required.')
    request, body = load(company, user, request_id, plan_digest, allow_cancelled=True)
    old = read(company.pk, request, 'cancelled')
    expected = {'company_id': str(company.pk), 'actor_id': str(user.pk), 'request_id': request, 'plan_digest': body['plan_digest']}
    if old:
        if old.payload != expected:raise AccountingError('Stored cancellation changed.')
        return result(company, request, plan_digest, 'CANCELLED', True)
    write(company.pk, request, 'cancelled', {'company_id': str(company.pk),
        'actor_id': str(user.pk), 'request_id': request, 'plan_digest': body['plan_digest']})
    return result(company, request, plan_digest, 'CANCELLED')


@transaction.atomic
def state(company_id, *, actor, provider_id, request_id):
    """Recover evidence without replaying approvals, money or desktop work."""
    company,user=authority(company_id,actor,provider_id)
    request=str(UUID(str(request_id)));prepared=read(company.pk,request,'prepared')
    if prepared is None:raise AccountingError('Scoped rehearsal unavailable.')
    if not isinstance(prepared.payload,dict):raise AccountingError('Invalid prepared evidence.')
    request,body=load(company,user,request,prepared.payload.get('plan_digest'),allow_cancelled=True)
    from django.utils.dateparse import parse_datetime
    expires=parse_datetime(body['expires_at'])
    if expires is None or timezone.is_naive(expires):raise AccountingError('Invalid rehearsal expiry.')
    first=read(company.pk,request,'confirmation1');second=read(company.pk,request,'confirmation2')
    if first:approval(company,request,body,'confirmation1')
    if second:
        if first is None:raise AccountingError('Orphan second confirmation.')
        approval(company,request,body,'confirmation2')
    simulated=read(company.pk,request,'simulated');cancelled=read(company.pk,request,'cancelled')
    expected={'company_id':str(company.pk),'actor_id':str(user.pk),'request_id':request,'plan_digest':body['plan_digest']}
    if simulated and (second is None or simulated.payload!={**expected,'status':'SIMULATED_ONLY'}):raise AccountingError('Simulation evidence changed.')
    if cancelled and cancelled.payload!=expected:raise AccountingError('Cancellation evidence changed.')
    expired=timezone.now()>=expires
    status='CANCELLED' if cancelled else 'SIMULATED_ONLY' if simulated else 'EXPIRED' if expired else 'CONFIRMED_2' if second else 'CONFIRMED_1' if first else 'PREPARED'
    return {**result(company,request,body['plan_digest'],status),'intent':body['intent'],'expires_at':body['expires_at'],
            'read_only':True,'confirmations_restored':False,'recorded_confirmations':int(bool(first))+int(bool(second)),
            'next_step':1 if status=='PREPARED' else 2 if status=='CONFIRMED_1' else None,
            'can_simulate':status=='CONFIRMED_2','can_cancel':status!='CANCELLED'}
