"""Owner-reviewed initial FX posting of existing drafts, not revaluation or payment.
Rates are declared evidence, never labelled official or independently verified.
"""
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP, localcontext
import re
from uuid import UUID, uuid5
from django.db import transaction
from django.utils import timezone
from apps.core_erp.outbox_models import OutboxEvent
from .exceptions import AccountingError
from .integrity import fingerprint
from .models import JournalEntry, LedgerEntry, FiscalPeriod
from .validation import lock_company, current_actor, money

NS=UUID('139789ed-3e5f-44db-b02a-aa6f3abaf588')
REVIEW='accounting.fx.reviewed.v1'
POSTED='accounting.fx.posted.v1'
QUOTE='accounting.fx.quote-declared.v1'

def uid(v):
    if not isinstance(v,str) or str(UUID(v))!=v:raise AccountingError('Canonical FX identifier required.')
    return v

def latest(company,entry_id):
    return OutboxEvent.objects.filter(event_type=REVIEW,domain='accounting',aggregate_root=entry_id,payload__company_id=str(company.pk)).order_by('-payload__revision').first()

def source(company,actor,entry_id):
    entry=JournalEntry.plain_objects.select_for_update().filter(pk=UUID(uid(entry_id)),tenant=company).first()
    if entry is None or entry.created_by_id!=actor.pk or entry.is_reversal or entry.currency not in {'USD','EUR'} or entry.base_currency!='COP' or company.currency!='COP':raise AccountingError('Own USD/EUR draft with COP base required.')
    from apps.core_erp.fx.models import Currency
    if Currency.objects.filter(code__in=[entry.currency,'COP'],is_active=True).count()!=2:raise AccountingError('Active transaction and base currencies required.')
    lines=list(LedgerEntry.plain_objects.select_for_update().filter(journal_entry=entry).select_related('account__chart_of_accounts').order_by('pk')[:101])
    if not 2<=len(lines)<=100:raise AccountingError('Between two and100 FX lines required.')
    from .ledger_engine import LedgerEngine
    LedgerEngine.validate_balance(entry,lines)
    for line in lines:
        if line.tenant_id!=company.pk or line.account.tenant_id!=company.pk or line.account.chart_of_accounts.tenant_id!=company.pk or not line.account.is_active or line.currency!=entry.currency:raise AccountingError('Scoped active FX accounts required.')
    snapshot={'entry_id':entry_id,'date':entry.date.isoformat(),'period_id':str(entry.period_id),'description':entry.description,'reference':entry.reference,'currency':entry.currency,'base_currency':entry.base_currency,'created_by':str(actor.pk),'lines':[{'line_id':str(r.pk),'account_id':str(r.account_id),'debit':format(r.debit_amount,'.2f'),'credit':format(r.credit_amount,'.2f'),'currency':r.currency,'description':r.description} for r in lines]}
    return entry,snapshot

def quote(value,snapshot):
    fields={'base_currency','target_currency','rate','source_reference','source_version','observed_at','valid_from','valid_until','evidence_digest'}
    if not isinstance(value,dict) or set(value)!=fields:raise AccountingError('Explicit bounded FX quote required.')
    if value['base_currency']!=snapshot['currency'] or value['target_currency']!='COP':raise AccountingError('Quote direction differs from journal.')
    if not isinstance(value['rate'],str) or not re.fullmatch(r'(?:0|[1-9][0-9]{0,8})\.[0-9]{6}',value['rate']) or Decimal(value['rate'])<=0:raise AccountingError('Positive rate as exact six-decimal text required.')
    for key in ('source_reference','source_version'):
        if not isinstance(value[key],str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}',value[key]):raise AccountingError('Bounded source reference/version required; no credentials.')
    if not isinstance(value['evidence_digest'],str) or not re.fullmatch('[0-9a-f]{64}',value['evidence_digest']):raise AccountingError('Source evidence digest required.')
    start=date.fromisoformat(value['valid_from']);end=date.fromisoformat(value['valid_until']);day=date.fromisoformat(snapshot['date'])
    if start.isoformat()!=value['valid_from'] or end.isoformat()!=value['valid_until'] or not start<=day<=end or (end-start).days>366:raise AccountingError('Quote validity must cover the journal date within367 days.')
    observed=datetime.fromisoformat(value['observed_at'])
    if len(value['observed_at'])>40 or observed.tzinfo is None or observed>timezone.now():raise AccountingError('Explicit nonfuture observed timestamp required.')
    return dict(value)

def quote_record(company,terms,create=False):
    identity={'company_id':str(company.pk),**{k:terms[k] for k in ('base_currency','target_currency','source_reference','source_version')}}
    identifier=uuid5(NS,'quote:'+fingerprint(identity))
    payload={'company_id':str(company.pk),'terms':{k:v for k,v in terms.items() if k!='observed_at'}}
    row=OutboxEvent.objects.filter(pk=identifier).first()
    if row is None and create:
        row=OutboxEvent.objects.create(id=identifier,event_type=QUOTE,domain='accounting',aggregate_root=str(company.pk),version=1,payload=payload)
    if row is None or row.event_type!=QUOTE or row.domain!='accounting' or row.aggregate_root!=str(company.pk) or row.version!=1 or row.payload!=payload:raise AccountingError('FX source version was changed or lost; declare a new source version explicitly.')
    return row

def valuation(snapshot,terms):
    result=[];debit=credit=Decimal('0.00');rate=Decimal(terms['rate'])
    with localcontext() as context:
        context.prec=38
        for row in snapshot['lines']:
            left=money(row['debit']);right=money(row['credit']);amount=left or right
            base=money((amount*rate).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))
            if base<=0:raise AccountingError('Rate rounds a positive line to zero; explicit adjustment required.')
            debit+=base if left else Decimal(0);credit+=base if right else Decimal(0)
            result.append({**row,'transaction_amount':format(amount,'.2f'),'base_amount':format(base,'.2f')})
    if debit!=credit:raise AccountingError('Per-line FX rounding does not balance; no balancing account is invented.')
    return {'lines':result,'total_debit_cop':format(debit,'.2f'),'total_credit_cop':format(credit,'.2f'),'rounding':'PER_LINE_HALF_UP'}

def checked(row,company):
    if row is None or row.event_type!=REVIEW or row.domain!='accounting' or row.version!=1:raise AccountingError('FX review unavailable.')
    body=row.payload.get('review')
    if not isinstance(body,dict) or body.get('company_id')!=str(company.pk) or row.payload.get('company_id')!=str(company.pk) or fingerprint(body)!=row.payload.get('review_digest') or row.payload.get('revision')!=body.get('revision') or type(body.get('revision')) is not int or body['revision']<1 or row.aggregate_root!=body['source']['entry_id'] or row.pk!=uuid5(NS,'review:'+body['source']['entry_id']+':'+str(body['revision'])):raise AccountingError('FX review integrity changed.')
    quote_record(company,body['quote'])
    if quote(body['quote'],body['source'])!=body['quote'] or valuation(body['source'],body['quote'])!=body['valuation']:raise AccountingError('FX valuation changed.')
    return body

@transaction.atomic
def review(company_id,*,actor,entry_id,terms,expected_revision,confirmed):
    company=lock_company(company_id);user=current_actor(actor);entry,snapshot=source(company,user,entry_id)
    if entry.is_posted or entry.financial_event_id and not entry.financial_event_id.startswith('reviewed-fx-pending:'):raise AccountingError('Unposted draft without another financial event required.')
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:raise AccountingError('First explicit FX confirmation and revision required.')
    if entry.date>timezone.localdate() or not FiscalPeriod.plain_objects.filter(pk=entry.period_id,tenant=company,status='open',period_start__lte=entry.date,period_end__gte=entry.date).exists():raise AccountingError('Open nonfuture economic date required.')
    terms=quote(terms,snapshot);values=valuation(snapshot,terms);old=latest(company,entry_id);revision=checked(old,company)['revision'] if old else 0
    if revision!=expected_revision:raise AccountingError('FX review changed; reload current state.')
    if (old is None and entry.financial_event_id) or (old is not None and entry.financial_event_id!='reviewed-fx-pending:'+str(old.pk)):raise AccountingError('FX draft reservation differs from its review.')
    quote_record(company,terms,create=True)
    body={'company_id':str(company.pk),'reviewed_by':str(user.pk),'revision':revision+1,'source':snapshot,'quote':terms,'valuation':values,'independently_verified':False}
    row=OutboxEvent.objects.create(id=uuid5(NS,'review:'+entry_id+':'+str(revision+1)),event_type=REVIEW,domain='accounting',aggregate_root=entry_id,version=1,payload={'company_id':str(company.pk),'revision':revision+1,'review':body,'review_digest':fingerprint(body)})
    entry.financial_event_id='reviewed-fx-pending:'+str(row.pk);entry.save(update_fields=['financial_event_id'])
    return {'company_id':str(company.pk),'review_id':str(row.pk),'preview':body,'ledger_written':False,'money_transferred':False,'rate_independently_verified':False}

def rate_for_post(company,actor,entry,review_id):
    row=latest(company,str(entry.pk));body=checked(row,company)
    _,snapshot=source(company,actor,str(entry.pk))
    if str(row.pk)!=uid(review_id) or entry.financial_event_id!='reviewed-fx:'+str(row.pk) or body['reviewed_by']!=str(actor.pk) or body['source']!=snapshot:raise AccountingError('Current owner-reviewed FX source required.')
    if entry.exchange_rate not in (Decimal('1'),Decimal(body['quote']['rate'])):raise AccountingError('Draft rate conflicts with reviewed rate.')
    return Decimal(body['quote']['rate'])

def result(company,user,row,proof,replayed):
    body=checked(row,company);entry,snapshot=source(company,user,body['source']['entry_id'])
    expected={'company_id':str(company.pk),'entry_id':str(entry.pk),'review_id':str(row.pk),'review_digest':fingerprint(body),'journal_hash':entry.system_hash}
    if proof is None or proof.event_type!=POSTED or proof.domain!='accounting' or proof.version!=1 or proof.pk!=uuid5(NS,'posted:'+str(entry.pk)) or proof.aggregate_root!=str(entry.pk) or proof.payload!=expected or not entry.is_posted or entry.financial_event_id!='reviewed-fx:'+str(row.pk) or entry.hash_version!='v2' or entry.compute_hash()!=entry.system_hash or entry.exchange_rate!=Decimal(body['quote']['rate']) or snapshot!=body['source']:raise AccountingError('Posted FX evidence changed; reconciliation required.')
    actual={str(r.pk):r for r in LedgerEntry.plain_objects.filter(journal_entry=entry,tenant=company)}
    if any(actual[r['line_id']].amount_base!=Decimal(r['base_amount']) or actual[r['line_id']].amount_transaction!=Decimal(r['transaction_amount']) for r in body['valuation']['lines']):raise AccountingError('Posted FX values differ from review.')
    reversals=list(JournalEntry.plain_objects.filter(tenant=company,reversed_entry_id=entry.pk,is_posted=True)[:2])
    if len(reversals)>1:raise AccountingError('Multiple FX reversals require reconciliation.')
    if reversals:
        reverse=reversals[0]
        from .ledger_engine import historical_reversal_valuation
        if reverse.compute_hash()!=reverse.system_hash:raise AccountingError('FX reversal hash changed.')
        historical_reversal_valuation(reverse,list(LedgerEntry.plain_objects.filter(journal_entry=reverse).select_related('account')))
    return {'schema':'sgacd-reviewed-fx-result-v1','company_id':str(company.pk),'entry_id':str(entry.pk),'journal_id':str(entry.pk),'review_id':str(row.pk),'journal_hash':entry.system_hash,'currency':entry.currency,'base_currency':'COP','exchange_rate':body['quote']['rate'],'source_reference':body['quote']['source_reference'],'source_version':body['quote']['source_version'],'total_debit_cop':body['valuation']['total_debit_cop'],'total_credit_cop':body['valuation']['total_credit_cop'],'original_reversed':bool(reversals),'replayed':replayed,'ledger_written':True,'money_transferred':False,'rate_independently_verified':False,'fiscal_accepted':False}

@transaction.atomic
def confirm(company_id,*,actor,entry_id,review_id,confirmed):
    company=lock_company(company_id);user=current_actor(actor);entry,_=source(company,user,entry_id);row=latest(company,entry_id);body=checked(row,company)
    if confirmed is not True or str(row.pk)!=uid(review_id) or body['reviewed_by']!=str(user.pk):raise AccountingError('Second confirmation of latest FX review by same owner required.')
    proof=OutboxEvent.objects.filter(pk=uuid5(NS,'posted:'+entry_id)).first()
    if proof:return result(company,user,row,proof,True)
    if entry.is_posted or entry.financial_event_id!='reviewed-fx-pending:'+str(row.pk):raise AccountingError('Draft was consumed or its FX reservation changed; no duplicate posting.')
    from .ledger_engine import LedgerEngine
    entry.financial_event_id='reviewed-fx:'+str(row.pk);entry.save(update_fields=['financial_event_id'])
    posted=LedgerEngine.post_entry(entry.pk,tenant_id=company.pk,actor=user,fx_review_id=str(row.pk))
    proof=OutboxEvent.objects.create(id=uuid5(NS,'posted:'+entry_id),event_type=POSTED,domain='accounting',aggregate_root=entry_id,version=1,payload={'company_id':str(company.pk),'entry_id':entry_id,'review_id':str(row.pk),'review_digest':fingerprint(body),'journal_hash':posted.system_hash})
    return result(company,user,row,proof,False)

@transaction.atomic
def state(company_id,*,actor,entry_id):
    company=lock_company(company_id);user=current_actor(actor);entry,snapshot=source(company,user,entry_id);row=latest(company,entry_id);body=checked(row,company) if row else None
    proof=OutboxEvent.objects.filter(pk=uuid5(NS,'posted:'+entry_id)).first()
    if entry.is_posted and (row is None or proof is None):raise AccountingError('Posted FX origin proof unavailable.')
    return {'company_id':str(company.pk),'entry_id':entry_id,'source':snapshot,'revision':body['revision'] if body else 0,'review_id':str(row.pk) if row else None,'preview':body,'source_matches_review':body['source']==snapshot if body else False,'applied':result(company,user,row,proof,True) if proof else None,'read_only':True,'confirmations_restored':False,'ledger_written':False,'money_transferred':False,'rate_independently_verified':False}


def verify_posted_origin(company,user,entry):
    review_id=entry.financial_event_id[len('reviewed-fx:'):]
    row=OutboxEvent.objects.filter(pk=UUID(uid(review_id))).first()
    proof=OutboxEvent.objects.filter(pk=uuid5(NS,'posted:'+str(entry.pk))).first()
    return result(company,user,row,proof,True)


@transaction.atomic
def sources(company_id,*,actor,after_id=None):
    """Bounded catalog of the current owner's unposted USD/EUR drafts."""
    from django.db.models import Q
    company=lock_company(company_id);user=current_actor(actor)
    if company.currency!='COP':raise AccountingError('COP company required.')
    query=JournalEntry.plain_objects.filter(tenant=company,created_by=user,is_posted=False,is_reversal=False,currency__in=['USD','EUR'],base_currency='COP',date__lte=timezone.localdate(),period__tenant=company,period__status='open').filter(Q(financial_event_id__isnull=True)|Q(financial_event_id='')|Q(financial_event_id__startswith='reviewed-fx-pending:'))
    if after_id is not None:query=query.filter(pk__gt=UUID(uid(after_id)))
    rows=list(query.order_by('pk')[:21])
    return {'company_id':str(company.pk),'sources':[{'entry_id':str(r.pk),'date':r.date.isoformat(),'currency':r.currency,'description':r.description,'review_pending':bool(r.financial_event_id)} for r in rows[:20]],'next_after':str(rows[19].pk) if len(rows)>20 else None,'read_only':True,'ledger_written':False,'money_transferred':False,'rate_independently_verified':False}
