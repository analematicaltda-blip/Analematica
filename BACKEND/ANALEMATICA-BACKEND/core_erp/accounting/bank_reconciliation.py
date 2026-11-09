"""Reviewed metadata reconciliation, not bank authentication or money movement.
All writes serialize on the accounting company. Raw CSV/transaction IDs are not
stored. Ledger lines remain unchanged. Releases append evidence, never erase it.
Authorization is enforced by owner-scoped HTTP boundaries; actor is explicit.
"""
import re
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID,uuid5
from django.db import transaction
from django.db.models import Q
from .bank_statement import compare_statement,cash_account
from .validation import lock_company,current_actor
from .exceptions import AccountingError
from .integrity import fingerprint
from .models import LedgerEntry,JournalEntry
from .invoice_intent import _money
from apps.core_erp.outbox_models import OutboxEvent

NS=UUID('76ff981c-4965-4e14-bbb8-438ba6d42b82')
REVIEW='accounting.bank-reconciliation.reviewed.v1'
APPLIED='accounting.bank-reconciliation.confirmed.v1'
REVIEW_V2='accounting.bank-reconciliation.reviewed.v2'
APPLIED_V2='accounting.bank-reconciliation.confirmed.v2'
CLAIM='accounting.bank-reconciliation.claimed.v1'
RELEASE_REVIEW='accounting.bank-reconciliation.release-reviewed.v1'
RELEASED='accounting.bank-reconciliation.released.v1'
REASONS={'WRONG_MATCH','SOURCE_WITHDRAWN','ACCOUNTING_CORRECTION'}

def digest(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise AccountingError('Explicit lowercase SHA256 digest required.')
    return value

def statement_id(company,account,source_digest):
    return uuid5(NS,'statement:'+str(UUID(str(company)))+':'+str(UUID(str(account)))+':'+digest(source_digest))

def _context(company_id,actor):
    company=lock_company(company_id);user=current_actor(actor)
    if company.currency!='COP' or getattr(user,'is_agent',False):raise AccountingError('Active personal reviewer and COP company required.')
    return company,user

def _latest(company,identifier):
    return OutboxEvent.objects.filter(event_type__in=(REVIEW,REVIEW_V2),aggregate_root=str(identifier),payload__company_id=str(company.pk),payload__statement_id=str(identifier)).order_by('-payload__revision').first()

def _review(row,company):
    if row is None:raise AccountingError('A persisted review is required.')
    p=row.payload;b=p.get('review')
    if row.event_type not in (REVIEW,REVIEW_V2) or row.version!=(2 if row.event_type==REVIEW_V2 else 1):raise AccountingError('Unsupported bank review version.')
    if not isinstance(b,dict) or b.get('company_id')!=str(company.pk) or fingerprint(b)!=p.get('review_digest') or b.get('statement_id')!=p.get('statement_id') or type(b.get('revision')) is not int or b['revision']<1 or b['revision']!=p.get('revision') or row.pk!=uuid5(NS,'review:'+b['statement_id']+':'+str(b['revision'])):
        raise AccountingError('Bank review evidence changed.')
    if str(statement_id(company.pk,b['account_id'],b['source_digest']))!=b['statement_id']:raise AccountingError('Statement source identity changed.')
    if row.event_type==REVIEW_V2:
        from .bank_resolutions import coverage
        if not isinstance(b.get('differences'),list) or b.get('coverage')!=coverage(b['rows'],b['differences']):raise AccountingError('Bank resolution coverage changed.')
    elif 'differences' in b or 'coverage' in b:raise AccountingError('Explicit resolutions require a v2 reader.')
    return b

def _claims(proof,body):
    expected=[]
    for row in body['rows']:
        identifier=uuid5(NS,'claim:'+str(proof.pk)+':'+row['ledger_line_id'])
        payload={'company_id':body['company_id'],'account_id':body['account_id'],'reconciliation_id':str(proof.pk),'statement_id':body['statement_id'],'review_digest':fingerprint(body),'ledger_line_id':row['ledger_line_id'],'transaction_ref_digest':row['transaction_ref_digest']}
        expected.append((identifier,payload))
    for row in body.get('differences',[]):
        identifier=uuid5(NS,'claim:'+str(proof.pk)+':difference:'+row['transaction_ref_digest'])
        payload={'company_id':body['company_id'],'account_id':body['account_id'],'reconciliation_id':str(proof.pk),'statement_id':body['statement_id'],'review_digest':fingerprint(body),'ledger_line_id':None,'transaction_ref_digest':row['transaction_ref_digest']}
        expected.append((identifier,payload))
    return expected

def _origin(company,proof):
    if proof is None or proof.event_type not in (APPLIED,APPLIED_V2) or proof.payload.get('company_id')!=str(company.pk):raise AccountingError('Reconciliation unavailable in company.')
    p=proof.payload;review=OutboxEvent.objects.filter(pk=p.get('review_id'),event_type__in=(REVIEW,REVIEW_V2)).first();body=_review(review,company)
    if proof.version!=(2 if proof.event_type==APPLIED_V2 else 1) or (proof.event_type==APPLIED_V2)!=(review.event_type==REVIEW_V2):raise AccountingError('Bank confirmation version mismatch.')
    if proof.pk!=uuid5(NS,'applied:'+str(review.pk)) or p.get('review_digest')!=fingerprint(body) or p.get('statement_id')!=body['statement_id'] or p.get('revision')!=body['revision']:
        raise AccountingError('Confirmed origin changed.')
    expected=_claims(proof,body);found={row.pk:row for row in OutboxEvent.objects.filter(pk__in=[identifier for identifier,_ in expected])}
    if len(found)!=len(expected) or any(found[i].event_type!=CLAIM or found[i].payload!=payload for i,payload in expected):raise AccountingError('Reconciliation claim evidence missing or changed.')
    return body

def _released(company,proof):
    row=OutboxEvent.objects.filter(pk=uuid5(NS,'released:'+str(proof.pk))).first()
    if row is None:return False
    p=row.payload;review=OutboxEvent.objects.filter(pk=p.get('review_id'),event_type=RELEASE_REVIEW,payload__company_id=str(company.pk)).first();b=review.payload.get('review') if review else None
    if row.event_type!=RELEASED or not isinstance(b,dict) or fingerprint(b)!=p.get('review_digest') or fingerprint(b)!=review.payload.get('review_digest') or b.get('reconciliation_id')!=str(proof.pk) or p.get('reconciliation_id')!=str(proof.pk) or b.get('origin_digest')!=fingerprint(proof.payload) or b.get('company_id')!=str(company.pk) or p.get('company_id')!=str(company.pk):raise AccountingError('Release evidence changed; no claim is silently freed.')
    return True

def _validate_rows(company,body,*,require_current_policy):
    if require_current_policy:
        account,policy=cash_account(company,body['account_id'])
        if policy['revision']!=body['policy_revision'] or policy['digest']!=body['policy_digest']:raise AccountingError('Cash-account classification changed after review.')
    checked=set()
    for expected in body['rows']:
        line=LedgerEntry.plain_objects.filter(pk=expected['ledger_line_id'],tenant=company,account_id=body['account_id']).select_related('journal_entry').first()
        if line is None:raise AccountingError('Matched ledger line missing or foreign.')
        journal=line.journal_entry
        if str(journal.tenant_id)!=str(company.pk) or not journal.is_posted or journal.is_reversal or journal.hash_version!='v2' or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=1 or line.currency!='COP' or line.amount_transaction!=line.debit_amount+line.credit_amount or line.amount_base!=line.debit_amount+line.credit_amount:
            raise AccountingError('Matched ledger line is not a qualified COP movement.')
        if str(journal.pk)!=expected['journal_id'] or journal.date.isoformat()!=expected['date'] or ('IN' if line.debit_amount>0 else 'OUT')!=expected['direction'] or format(line.debit_amount or line.credit_amount,'.2f')!=expected['amount']:raise AccountingError('Matched date/direction/amount changed.')
        if journal.pk not in checked:
            if journal.system_hash!=expected['journal_hash'] or journal.compute_hash()!=expected['journal_hash'] or JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id=journal.pk).exists():raise AccountingError('Matched original changed or was reversed; review required.')
            checked.add(journal.pk)

def _conflicts(company,body):
    rows=body['rows'];lines=[r['ledger_line_id'] for r in rows];refs=[r['transaction_ref_digest'] for r in rows+body.get('differences',[])]
    claims=list(OutboxEvent.objects.filter(event_type=CLAIM,payload__company_id=str(company.pk)).filter(Q(payload__ledger_line_id__in=lines)|Q(payload__transaction_ref_digest__in=refs))[:1001])
    if len(claims)>1000:raise AccountingError('Claim history exceeds this bounded review; separate reconciliation required.')
    seen=set()
    for claim in claims:
        identifier=claim.payload.get('reconciliation_id')
        if identifier in seen:continue
        seen.add(identifier);proof=OutboxEvent.objects.filter(pk=identifier,event_type__in=(APPLIED,APPLIED_V2)).first()
        _origin(company,proof)
        if not _released(company,proof):raise AccountingError('A transaction or ledger line already has an active reconciliation.')

def _result(company,proof,*,replayed):
    body=_origin(company,proof);released=_released(company,proof);valid=False
    if not released:
        try:_validate_rows(company,body,require_current_policy=False);valid=True
        except AccountingError:pass
    from .bank_resolutions import coverage
    complete=valid and not body.get('differences')
    assessment=body.get('period_assessment');period_current=None
    if assessment is not None:
        from .bank_period import assess
        try:period_current=assess(company,body['account_id'],assessment['terms'],body['rows'],body.get('differences',[]))==assessment
        except (AccountingError,ValueError,TypeError,ObjectDoesNotExist):period_current=False
    return {'period_assessment':assessment,'period_source_current':period_current,'period_reconciled':bool(complete and period_current and assessment['eligible_for_period_reconciliation']),'period_requires_review':bool(assessment and not released and not period_current),'coverage':coverage(body['rows'],body.get('differences',[])),'fully_reconciled':complete,'associations_confirmed':valid,'company_id':str(company.pk),'statement_id':body['statement_id'],'reconciliation_id':str(proof.pk),'review_id':proof.payload['review_id'],'matched_rows':len(body['rows']),'historically_confirmed':True,'reconciliation_confirmed':complete,'requires_review':not released and not valid,'released':released,'replayed':replayed,'bank_verified':False,'bank_connected':False,'raw_statement_stored':False,'derived_rows_stored':True,'ledger_written':False,'money_transferred':False}

@transaction.atomic
def review_reconciliation(company_id,*,actor,account_id,csv_text,evidence_digest,expected_revision,confirmed,resolutions=None,period=None):
    company,user=_context(company_id,actor)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:raise AccountingError('First explicit review and revision required.')
    digest(evidence_digest);comparison=compare_statement(company.pk,account_id=account_id,csv_text=csv_text)
    if not 1<=len(comparison['rows'])<=30 or resolutions is None and any(row['status']!='UNIQUE_CANDIDATE' for row in comparison['rows']):raise AccountingError('This reviewed batch requires1 to30 unique matched rows; resolve unmatched/ambiguous rows separately.')
    account,policy=cash_account(company,account_id);identifier=statement_id(company.pk,account.pk,comparison['source_digest'])
    old=_latest(company,identifier);previous=_review(old,company)['revision'] if old else 0
    if previous!=expected_revision:raise AccountingError('Statement review changed; recover its current state.')
    prior=OutboxEvent.objects.filter(event_type__in=(APPLIED,APPLIED_V2),payload__company_id=str(company.pk),payload__statement_id=str(identifier)).order_by('-payload__revision').first()
    if prior:
        _origin(company,prior)
        if not _released(company,prior):raise AccountingError('Statement is already confirmed; recover or explicitly release it.')
    rows=[] if resolutions is not None else [{k:row[k] for k in ['row','transaction_ref_digest','date','direction','amount']}|row['candidates'][0] for row in comparison['rows']]
    differences=[]
    if resolutions is not None:
        from .bank_resolutions import resolve
        rows,differences=resolve(comparison['rows'],resolutions)
    body={'company_id':str(company.pk),'account_id':str(account.pk),'statement_id':str(identifier),'source_digest':comparison['source_digest'],'reviewed_by':str(user.pk),'revision':previous+1,'evidence_digest':evidence_digest,'policy_revision':policy['revision'],'policy_digest':policy['digest'],'rows':rows,'currency':'COP','bank_verified':False}
    if resolutions is not None or period is not None:
        from .bank_resolutions import coverage
        body.update(differences=differences,coverage=coverage(rows,differences))
    if period is not None:
        from .bank_period import assess
        body['period_assessment']=assess(company,account.pk,period,rows,differences)
    _validate_rows(company,body,require_current_policy=True);_conflicts(company,body)
    row=OutboxEvent.objects.create(id=uuid5(NS,'review:'+str(identifier)+':'+str(previous+1)),event_type=REVIEW_V2 if resolutions is not None or period is not None else REVIEW,domain='accounting',aggregate_root=str(identifier),payload={'company_id':str(company.pk),'statement_id':str(identifier),'revision':previous+1,'review':body,'review_digest':fingerprint(body)},version=2 if resolutions is not None or period is not None else 1)
    return {'company_id':str(company.pk),'statement_id':str(identifier),'review_id':str(row.pk),'preview':body,'ledger_written':False,'bank_verified':False,'raw_statement_stored':False,'derived_rows_stored':True,'money_transferred':False}

@transaction.atomic
def confirm_reconciliation(company_id,*,actor,statement_id,review_id,confirmed):
    company,user=_context(company_id,actor)
    if confirmed is not True:raise AccountingError('Second explicit reconciliation confirmation required.')
    review=_latest(company,UUID(str(statement_id)));body=_review(review,company)
    if review.pk!=UUID(str(review_id)) or body['reviewed_by']!=str(user.pk):raise AccountingError('Current review by the same actor required.')
    identifier=uuid5(NS,'applied:'+str(review.pk));proof=OutboxEvent.objects.filter(pk=identifier).first()
    if proof:return _result(company,proof,replayed=True)
    _validate_rows(company,body,require_current_policy=True);_conflicts(company,body)
    if body.get('period_assessment') is not None:
        from .bank_period import assess
        if assess(company,body['account_id'],body['period_assessment']['terms'],body['rows'],body.get('differences',[]))!=body['period_assessment']:raise AccountingError('Period ledger history changed after review; recover and review again.')
    payload={'company_id':str(company.pk),'statement_id':body['statement_id'],'review_id':str(review.pk),'review_digest':fingerprint(body),'revision':body['revision']}
    # Write claims before the proof; the encompassing transaction is all-or-none.
    event_type=APPLIED_V2 if review.event_type==REVIEW_V2 else APPLIED
    proof=OutboxEvent(id=identifier,payload=payload,event_type=event_type)
    for key,value in _claims(proof,body):OutboxEvent.objects.create(id=key,event_type=CLAIM,domain='accounting',aggregate_root=body['statement_id'],payload=value,version=1)
    proof=OutboxEvent.objects.create(id=identifier,event_type=event_type,domain='accounting',aggregate_root=body['statement_id'],payload=payload,version=2 if event_type==APPLIED_V2 else 1)
    return _result(company,proof,replayed=False)

@transaction.atomic
def reconciliation_state(company_id,*,actor,account_id,source_digest):
    company,user=_context(company_id,actor);account=UUID(str(account_id));digest(source_digest)
    # Historical recovery need not keep an account active; ownership still must match.
    from .models import Account
    if not Account.plain_objects.filter(pk=account,tenant=company,chart_of_accounts__tenant=company).exists():raise AccountingError('Account unavailable in company.')
    identifier=statement_id(company.pk,account,source_digest);review=_latest(company,identifier);body=_review(review,company) if review else None
    applied=OutboxEvent.objects.filter(event_type__in=(APPLIED,APPLIED_V2),payload__company_id=str(company.pk),payload__statement_id=str(identifier)).order_by('-payload__revision').first()
    return {'company_id':str(company.pk),'statement_id':str(identifier),'account_id':str(account),'source_digest':source_digest,'revision':body['revision'] if body else 0,'review_id':str(review.pk) if review else None,'preview':body,'reviewed_by_current_owner':bool(body and body['reviewed_by']==str(user.pk)),'applied':_result(company,applied,replayed=True) if applied else None,'read_only':True,'confirmations_restored':False,'bank_verified':False}

@transaction.atomic
def review_release(company_id,*,actor,reconciliation_id,reason_code,evidence_digest,confirmed):
    company,user=_context(company_id,actor)
    if confirmed is not True or reason_code not in REASONS:raise AccountingError('Explicit release review and supported reason required.')
    digest(evidence_digest);proof=OutboxEvent.objects.filter(pk=UUID(str(reconciliation_id)),event_type__in=(APPLIED,APPLIED_V2),payload__company_id=str(company.pk)).first();body=_origin(company,proof)
    if _released(company,proof):raise AccountingError('Reconciliation already released; no new release review.')
    release={'company_id':str(company.pk),'statement_id':body['statement_id'],'reconciliation_id':str(proof.pk),'reviewed_by':str(user.pk),'reason_code':reason_code,'evidence_digest':evidence_digest,'origin_digest':fingerprint(proof.payload)}
    identifier=uuid5(NS,'release-review:'+fingerprint(release));payload={'company_id':str(company.pk),'review':release,'review_digest':fingerprint(release)}
    row=OutboxEvent.objects.filter(pk=identifier).first()
    if row and (row.event_type!=RELEASE_REVIEW or row.payload!=payload):raise AccountingError('Release review identity conflict.')
    if row is None:OutboxEvent.objects.create(id=identifier,event_type=RELEASE_REVIEW,domain='accounting',aggregate_root=body['statement_id'],payload=payload,version=1)
    return {'company_id':str(company.pk),'review_id':str(identifier),'reconciliation_id':str(proof.pk),'preview':release,'ledger_written':False,'bank_verified':False,'money_transferred':False}

@transaction.atomic
def confirm_release(company_id,*,actor,review_id,confirmed):
    company,user=_context(company_id,actor)
    if confirmed is not True:raise AccountingError('Second explicit release confirmation required.')
    row=OutboxEvent.objects.filter(pk=UUID(str(review_id)),event_type=RELEASE_REVIEW,payload__company_id=str(company.pk)).first();body=row.payload.get('review') if row else None
    if not isinstance(body,dict) or fingerprint(body)!=row.payload.get('review_digest') or body.get('reviewed_by')!=str(user.pk):raise AccountingError('Release review or reviewer changed.')
    proof=OutboxEvent.objects.filter(pk=body['reconciliation_id'],event_type__in=(APPLIED,APPLIED_V2),payload__company_id=str(company.pk)).first();_origin(company,proof)
    if body['origin_digest']!=fingerprint(proof.payload):raise AccountingError('Confirmed origin changed before release.')
    identifier=uuid5(NS,'released:'+str(proof.pk));existing=OutboxEvent.objects.filter(pk=identifier).first()
    if existing:
        if existing.payload.get('review_id')!=str(row.pk):raise AccountingError('Another release was already confirmed.')
        return _result(company,proof,replayed=True)
    payload={'company_id':str(company.pk),'reconciliation_id':str(proof.pk),'review_id':str(row.pk),'review_digest':fingerprint(body)}
    OutboxEvent.objects.create(id=identifier,event_type=RELEASED,domain='accounting',aggregate_root=body['statement_id'],payload=payload,version=1)
    return _result(company,proof,replayed=False)

@transaction.atomic
def reconciliation_sources(company_id,*,actor):
    from . import ratios
    from .models import Account
    company,user=_context(company_id,actor);policy=ratios.describe(ratios.latest(company.pk))
    if policy is None:raise AccountingError('Reviewed cash-account classification required.')
    mapping=ratios.normalize(company.pk,policy['mapping'])
    rows=list(Account.plain_objects.filter(tenant=company,pk__in=mapping['cash_equivalents']).order_by('code','pk')[:201])
    return {'company_id':str(company.pk),'read_only':True,'accounts':[{'id':str(row.pk),'code':row.code,'name':row.name} for row in rows[:200]],'truncated':len(rows)>200,'limit':200,'policy_revision':policy['revision'],'bank_verified':False}
