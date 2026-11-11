"""Reviewed liquidity classification and exact primary-ledger analytics.

Authorization belongs to the verified company adapter. Internal services must
supply that company and an active reviewer. No money is transferred here.
"""
import hashlib
import json
import re
from uuid import UUID
from datetime import date
from decimal import Decimal,localcontext,ROUND_HALF_UP
from django.db import transaction
from .models import Account,JournalEntry
from .ratio_models import AccountingRatioPolicy
from .reports_engine import ReportsEngine
from .validation import lock_company,current_actor,exact_arithmetic
from .exceptions import AccountingError

ROLES={'cash_equivalents':'ASSET','temporary_investments':'ASSET',
       'immediate_receivables':'ASSET','current_liabilities':'LIABILITY'}
ZERO=Decimal('0.00')


def normalize(company_id,mapping):
    if not isinstance(mapping,dict) or set(mapping)!=set(ROLES):
        raise AccountingError('Explicit classification of all four liquidity buckets is required.')
    normalized={};seen=set()
    for role,kind in ROLES.items():
        values=mapping[role]
        if not isinstance(values,list) or len(values)>1000:
            raise AccountingError('Account buckets must be bounded lists of UUIDs.')
        ids=[]
        for value in values:
            if not isinstance(value,str):raise AccountingError('Account UUID strings are required.')
            try:identifier=str(UUID(value))
            except (TypeError,ValueError,AttributeError):raise AccountingError('Invalid account UUID.') from None
            if identifier in seen:raise AccountingError('An account cannot be counted twice.')
            seen.add(identifier);ids.append(identifier)
        accounts=list(Account.plain_objects.filter(tenant_id=company_id,pk__in=ids,
                     chart_of_accounts__tenant_id=company_id,is_active=True,type=kind).values_list('pk',flat=True))
        if len(accounts)!=len(ids):raise AccountingError('Foreign, inactive or incorrectly typed account classification.')
        normalized[role]=sorted(ids)
    if not normalized['current_liabilities'] or not any(normalized[r] for r in ROLES if r!='current_liabilities'):
        raise AccountingError('Explicit asset and current-liability accounts are required.')
    return normalized


def digest(policy):
    payload={'tenant_id':str(policy.tenant_id),'revision':policy.revision,'mapping':policy.mapping,
             'reviewer_id':policy.reviewer_id,'evidence_digest':policy.evidence_digest}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def describe(policy):
    if policy is None:return None
    if digest(policy)!=policy.digest:raise AccountingError('Classification integrity mismatch.')
    return {'id':str(policy.pk),'revision':policy.revision,'mapping':policy.mapping,
            'reviewer_id':policy.reviewer_id,'evidence_digest':policy.evidence_digest,
            'digest':policy.digest,'created_at':policy.created_at.isoformat(),
            'verification':'reviewer_declared_not_independent_attestation'}


def latest(company_id):
    return AccountingRatioPolicy.objects.filter(tenant_id=company_id).order_by('-revision').first()


@transaction.atomic
def configure(company_id,*,actor,mapping,evidence_digest,expected_revision,confirmed):
    company=lock_company(company_id);reviewer=current_actor(actor)
    if confirmed is not True:raise AccountingError('Explicit accounting classification review is required.')
    if type(expected_revision) is not int or expected_revision<0:
        raise AccountingError('An explicit nonnegative expected revision is required.')
    if not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):
        raise AccountingError('A lowercase SHA-256 evidence digest is required.')
    current=latest(company.pk)
    if current:describe(current)
    if expected_revision!=(current.revision if current else 0):
        raise AccountingError('The classification changed; reload before reviewing again.')
    normalized=normalize(company.pk,mapping)
    policy=AccountingRatioPolicy(tenant=company,revision=expected_revision+1,mapping=normalized,
                                 evidence_digest=evidence_digest,reviewer=reviewer)
    policy.digest=digest(policy);policy.save()
    return describe(policy)


@transaction.atomic
@exact_arithmetic
def quick_ratio(company_id,cutoff,*,policy_revision=None):
    if type(cutoff) is not date:raise AccountingError('An economic cutoff date is required.')
    company=lock_company(company_id)
    if policy_revision is not None and (type(policy_revision) is not int or policy_revision<1):
        raise AccountingError('A positive explicit policy revision is required.')
    policy=(AccountingRatioPolicy.objects.filter(tenant_id=company.pk,revision=policy_revision).first()
            if policy_revision is not None else latest(company.pk))
    if policy_revision is not None and policy is None:
        raise AccountingError('The requested company policy revision is unavailable.')
    tail=JournalEntry.plain_objects.filter(tenant=company,is_posted=True).order_by('-posted_at','-pk').first()
    snapshot={'database':'primary','consistency':'company_lock_shared_with_posting','ledger_tail_id':str(tail.pk) if tail else None,'ledger_tail_hash':tail.system_hash if tail else None,'historical_publication_snapshot':False}
    base={'tenant_id':str(company.pk),'currency':company.currency,'cutoff_date':cutoff.isoformat(),
          'read_only':True,'posted_only':True,'valuation':'base_currency','ledger_written':False,'money_transferred':False,'snapshot':snapshot,'unit':'times','formula':'(cash_equivalents+temporary_investments+immediate_receivables)/current_liabilities',
          'source':'primary_posted_ledger','policy':describe(policy),'value':None,
          'classification_scope':'selected_accounts_reviewed_by_owner_not_independently_certified',
          'historical_policy':'explicit_reviewed_revision_applied_to_cutoff' if policy_revision is not None else 'latest_reviewed_classification_applied_to_cutoff',
          'reconstruction':'current_posted_ledger_by_economic_date_not_original_publication_snapshot'}
    if policy is None:return {**base,'unavailable_reason':'REVIEWED_CLASSIFICATION_REQUIRED'}
    mapping=normalize(company.pk,policy.mapping)
    if JournalEntry.plain_objects.filter(tenant_id=company.pk,is_posted=True,date__lte=cutoff).exclude(base_currency=company.currency).exists():
        raise AccountingError('Historical base currencies require reconciliation.')
    rows=ReportsEngine._totals(company.pk,cutoff,database='default')
    balances={str(row['account_id']):row['debit']-row['credit'] for row in rows}
    sources={};totals={}
    for role,ids in mapping.items():
        sources[role]=[]
        for identifier in ids:
            amount=balances.get(identifier,ZERO)*(1 if ROLES[role]=='ASSET' else -1)
            sources[role].append({'account_id':identifier,'balance':format(amount,'.2f')})
        totals[role]=sum((Decimal(r['balance']) for r in sources[role]),ZERO)
    base.update({'sources':sources,'totals':{k:format(v,'.2f') for k,v in totals.items()}})
    if any(Decimal(r['balance'])<0 for entries in sources.values() for r in entries):
        return {**base,'unavailable_reason':'NEGATIVE_ACCOUNT_BALANCE_REQUIRES_REVIEW'}
    if totals['current_liabilities']<=ZERO:return {**base,'unavailable_reason':'NON_POSITIVE_CURRENT_LIABILITIES'}
    with localcontext() as ctx:
        ctx.prec=50
        value=(sum((totals[r] for r in ROLES if r!='current_liabilities'),ZERO)/totals['current_liabilities']).quantize(Decimal('0.0001'),rounding=ROUND_HALF_UP)
    return {**base,'value':format(value,'.4f'),'unavailable_reason':None}

@transaction.atomic
def history(company_id,*,before_revision=None,limit=20):
    """Bounded keyset history, including inactive old mappings without reclassifying them."""
    company=lock_company(company_id)
    if type(limit) is not int or not 1<=limit<=50:
        raise AccountingError('History limit must be between 1 and 50.')
    if before_revision is not None and (type(before_revision) is not int or before_revision<1):
        raise AccountingError('A positive revision cursor is required.')
    query=AccountingRatioPolicy.objects.filter(tenant_id=company.pk).order_by('-revision')
    if before_revision is not None:query=query.filter(revision__lt=before_revision)
    rows=list(query[:limit+1]);page=rows[:limit]
    # Validate the whole returned page before exposing any of it.
    return {'tenant_id':str(company.pk),'results':[describe(row) for row in page],
            'next_before':page[-1].revision if len(rows)>limit else None,
            'read_only':True,'verification':'local_digest_not_independent_signature'}
