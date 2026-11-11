"""Reviewed many-to-many bank matching in bounded, fully balanced same-date groups.
Metadata only; no payment, invoice settlement, FX, inferred dates or ledger writes.
"""
from uuid import UUID,uuid5
from datetime import date
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from . import bank_reconciliation as legacy
from .bank_statement import compare_statement,cash_account
from .models import LedgerEntry,JournalEntry
from .exceptions import AccountingError
from .integrity import fingerprint
from .invoice_intent import _money,_format_money
from apps.core_erp.outbox_models import OutboxEvent

NS=UUID('740ee774-f951-4e30-a08a-42c348711a40')
REVIEW='accounting.bank-group.reviewed.v1'
APPLIED='accounting.bank-group.confirmed.v1'
RELEASE_REVIEW='accounting.bank-group.release-reviewed.v1'
RELEASED='accounting.bank-group.released.v1'

def ident(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise AccountingError('Canonical group/line identifier required.')
    return value

def latest(company,statement):return OutboxEvent.objects.filter(event_type=REVIEW,payload__company_id=str(company.pk),aggregate_root=str(statement)).order_by('-payload__revision').first()

def sources_locked(company,account_id,csv_text,ledger_since=None):
    compared=compare_statement(company.pk,account_id=account_id,csv_text=csv_text)
    from .bank_statement import require_booked
    require_booked(compared)
    if len(compared['rows'])>30:raise AccountingError('At most30 bank rows per grouped reconciliation.')
    account,policy=cash_account(company,account_id);start=min(r['date'] for r in compared['rows']);end=max(r['date'] for r in compared['rows'])
    if ledger_since is not None:
        parsed=date.fromisoformat(ledger_since)
        if parsed.isoformat()!=ledger_since or ledger_since>start or (date.fromisoformat(end)-parsed).days>366:raise AccountingError('Explicit canonical source window of at most367 days required.')
        start=ledger_since
    query=LedgerEntry.plain_objects.filter(tenant=company,account=account,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__is_reversal=False,journal_entry__date__gte=start,journal_entry__date__lte=end).select_related('journal_entry').order_by('pk')
    lines=list(query[:201])
    if len(lines)>200:raise AccountingError('Narrow the statement dates; at most200 cash candidates are supported.')
    reversed_ids=set(JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id__in=[line.journal_entry_id for line in lines]).values_list('reversed_entry_id',flat=True))
    ledger=[{'ledger_line_id':str(line.pk),'journal_id':str(line.journal_entry_id),'journal_hash':line.journal_entry.system_hash,'date':line.journal_entry.date.isoformat(),'direction':'IN' if line.debit_amount>0 else 'OUT','amount':format(line.debit_amount or line.credit_amount,'.2f')} for line in lines if line.journal_entry_id not in reversed_ids]
    legacy._validate_rows(company,{'account_id':str(account.pk),'rows':ledger},require_current_policy=False)
    from .bank_capacity import balances
    capacity={r['ledger_line_id']:r for r in balances(company,ledger)}
    ledger=[{**r,**{k:capacity[r['ledger_line_id']][k] for k in ('reserved_amount','available_amount')}} for r in ledger]
    bank=[{k:r[k] for k in ('row','transaction_ref_digest','date','direction','amount')} for r in compared['rows']]
    return {'ledger_since':start,'company_id':str(company.pk),'account_id':str(account.pk),'source_digest':compared['source_digest'],'policy_revision':policy['revision'],'policy_digest':policy['digest'],'bank_rows':bank,'ledger_lines':ledger,'read_only':True,'ledger_written':False,'money_transferred':False,'bank_verified':False,'raw_statement_stored':False}

@transaction.atomic
def sources(company_id,*,actor,account_id,csv_text,ledger_since=None):
    company,_=legacy._context(company_id,actor);return sources_locked(company,account_id,csv_text,ledger_since)

def selection(source,groups):
    if not isinstance(groups,list) or not 1<=len(groups)<=20:raise AccountingError('One to20 explicit groups required.')
    bank={r['row']:r for r in source['bank_rows']};ledger={r['ledger_line_id']:r for r in source['ledger_lines']};seen_bank=set();seen_lines=set();seen_groups=set();normalized=[]
    partial=all(isinstance(g,dict) and 'ledger_allocations' in g for g in groups)
    for group in groups:
        required={'group_id','bank_rows','ledger_allocations' if partial else 'ledger_line_ids'}
        if not isinstance(group,dict) or set(group)!=required:raise AccountingError('Do not mix whole-line and amount-allocation modes.')
        gid=ident(group['group_id']);bs=group['bank_rows'];allocations=group.get('ledger_allocations')
        if partial:
            if not isinstance(allocations,list) or not 1<=len(allocations)<=60 or any(not isinstance(a,dict) or set(a)!={'ledger_line_id','amount'} for a in allocations):raise AccountingError('Explicit line and positive exact allocated amount required.')
            ls=[a['ledger_line_id'] for a in allocations]
            if any(_money(a['amount'])<=0 for a in allocations):raise AccountingError('Zero/negative allocations cannot reserve capacity.')
        else:ls=group['ledger_line_ids']
        if gid in seen_groups or not isinstance(bs,list) or not 1<=len(bs)<=30 or not isinstance(ls,list) or not 1<=len(ls)<=60 or any(type(i) is not int or i not in bank for i in bs) or len(set(bs))!=len(bs) or any(not isinstance(i,str) or i not in ledger for i in ls) or len(set(ls))!=len(ls) or seen_bank.intersection(bs) or not partial and seen_lines.intersection(ls):raise AccountingError('Unique actual sources without bank-row reuse required.')
        bank_records=[bank[i] for i in bs];book_records=[ledger[i] for i in ls];records=bank_records+book_records;bank_day=bank_records[0]['date']
        if len({r['direction'] for r in records})!=1 or len({r['date'] for r in bank_records})!=1:raise AccountingError('A group needs one bank date and one direction; no netting.')
        if partial:
            if any(not source.get('ledger_since',bank_day)<=r['date']<=bank_day for r in book_records):raise AccountingError('The explicit source window must cover every original cash date.')
        elif len({r['date'] for r in records})!=1:raise AccountingError('Whole-line mode requires the same date.')
        bank_total=sum(_money(r['amount']) for r in bank_records);book_total=sum(_money(a['amount']) for a in allocations) if partial else sum(_money(r['amount']) for r in book_records)
        if bank_total!=book_total:raise AccountingError('Bank rows and allocated amounts must reconcile exactly.')
        result={'group_id':gid,'bank_rows':sorted(bs),'ledger_line_ids':sorted(ls),'date':bank_day,'direction':bank_records[0]['direction'],'amount':_format_money(bank_total)}
        if partial:result['ledger_allocations']=sorted(allocations,key=lambda a:a['ledger_line_id'])
        normalized.append(result);seen_groups.add(gid);seen_bank.update(bs);seen_lines.update(ls)
    if seen_bank!=set(bank) or len(seen_lines)>60:raise AccountingError('Cover every bank row once; at most60 selected lines.')
    selected=[ledger[i] for i in sorted(seen_lines)]
    if partial:
        from .bank_capacity import totals
        for key,value in totals(normalized,selected).items():
            if _money(value)>_money(ledger[key].get('available_amount',ledger[key]['amount'])):raise AccountingError('Selection exceeds available capacity.')
    return sorted(normalized,key=lambda g:g['group_id']),selected

def checked(row,company):
    if row is None or row.event_type!=REVIEW or row.version!=1 or row.domain!='accounting':raise AccountingError('Grouped review unavailable.')
    p=row.payload;b=p.get('review')
    if not isinstance(b,dict) or b.get('company_id')!=str(company.pk) or p.get('company_id')!=str(company.pk) or p.get('revision')!=b.get('revision') or type(b.get('revision')) is not int or b['revision']<1 or fingerprint(b)!=p.get('review_digest') or row.aggregate_root!=b['statement_id'] or row.pk!=uuid5(NS,'review:'+b['statement_id']+':'+str(b['revision'])) or b['statement_id']!=str(legacy.statement_id(company.pk,b['account_id'],b['source_digest'])):raise AccountingError('Grouped review evidence changed.')
    groups,lines=selection({'ledger_since':b.get('ledger_since',min(r['date'] for r in b['bank_rows'])),'bank_rows':b['bank_rows'],'ledger_lines':b['ledger_lines']},[{k:g[k] for k in ('group_id','bank_rows','ledger_allocations' if 'allocation_totals' in b else 'ledger_line_ids')} for g in b['groups']])
    if 'allocation_totals' in b:
        from .bank_capacity import totals
        if totals(groups,lines)!=b['allocation_totals']:raise AccountingError('Allocated capacity evidence changed.')
    if groups!=b['groups'] or lines!=b['ledger_lines']:raise AccountingError('Grouped review no longer conserves its sources.')
    return b

def claims(proof,body):
    result=[]
    for kind,items,key in [('bank',body['bank_rows'],'transaction_ref_digest'),('line',body['ledger_lines'],'ledger_line_id')]:
        for row in items:
            identifier=uuid5(NS,'claim:'+str(proof.pk)+':'+kind+':'+str(row[key]));payload={'company_id':body['company_id'],'account_id':body['account_id'],'reconciliation_id':str(proof.pk),'statement_id':body['statement_id'],'review_digest':fingerprint(body),'ledger_line_id':row[key] if kind=='line' else None,'transaction_ref_digest':row[key] if kind=='bank' else None}
            if kind=='line' and 'allocation_totals' in body:payload['allocated_amount']=body['allocation_totals'][row[key]]
            result.append((identifier,payload))
    return result

def origin(company,proof):
    if proof is None or proof.event_type!=APPLIED or proof.version!=1 or proof.payload.get('company_id')!=str(company.pk):raise AccountingError('Grouped confirmation unavailable.')
    review=OutboxEvent.objects.filter(pk=proof.payload.get('review_id'),event_type=REVIEW).first();body=checked(review,company)
    if proof.domain!='accounting' or proof.aggregate_root!=body['statement_id'] or proof.payload.get('revision')!=body['revision'] or proof.pk!=uuid5(NS,'applied:'+str(review.pk)) or proof.payload.get('review_digest')!=fingerprint(body) or proof.payload.get('statement_id')!=body['statement_id']:raise AccountingError('Grouped origin changed.')
    expected=claims(proof,body);found={r.pk:r for r in OutboxEvent.objects.filter(pk__in=[i for i,_ in expected])}
    if len(found)!=len(expected) or any(found[i].event_type!=legacy.CLAIM or found[i].payload!=payload for i,payload in expected):raise AccountingError('Grouped claim evidence missing or changed.')
    return body

def released(company,proof):
    row=OutboxEvent.objects.filter(pk=uuid5(NS,'released:'+str(proof.pk))).first()
    if row is None:return False
    review=OutboxEvent.objects.filter(pk=row.payload.get('review_id'),event_type=RELEASE_REVIEW).first();body=review.payload.get('review') if review else None
    if row.event_type!=RELEASED or not isinstance(body,dict) or body.get('company_id')!=str(company.pk) or body.get('reconciliation_id')!=str(proof.pk) or body.get('origin_digest')!=fingerprint(proof.payload) or fingerprint(body)!=review.payload.get('review_digest') or row.payload.get('review_digest')!=fingerprint(body):raise AccountingError('Grouped release evidence changed.')
    return True

def validate_lines(company,body,current_policy):
    legacy._validate_rows(company,{**body,'rows':body['ledger_lines']},require_current_policy=current_policy)

def conflicts(company,body):
    if 'allocation_totals' not in body:return legacy._conflicts(company,{**body,'rows':body['ledger_lines'],'differences':body['bank_rows']})
    legacy._conflicts(company,{**body,'rows':[],'differences':body['bank_rows']})
    from .bank_capacity import balances
    for row in balances(company,body['ledger_lines']):
        if _money(body['allocation_totals'][row['ledger_line_id']])>_money(row['available_amount']):raise AccountingError('Capacity changed after review; the original line cannot be overallocated.')

def period_assessment(company,body,terms):
    from .bank_period import assess
    assessment=assess(company,body['account_id'],terms,body['bank_rows'],[],matched_line_ids=[line['ledger_line_id'] for line in body['ledger_lines']])
    # Selecting a line does not mean allocating its whole original amount.
    complete=all(_money(body['allocation_totals'][line['ledger_line_id']])==_money(line['amount']) for line in body['ledger_lines']) if 'allocation_totals' in body else True
    return {**assessment,'group_allocations_complete':complete,'eligible_for_period_reconciliation':assessment['eligible_for_period_reconciliation'] and complete}

def result(company,proof,replayed):
    body=origin(company,proof);freed=released(company,proof);valid=False
    if not freed:
        try:validate_lines(company,body,False);valid=True
        except (AccountingError,ObjectDoesNotExist):pass
    from .bank_capacity import balances
    current=balances(company,body['ledger_lines']) if valid else None
    assessment=body.get('period_assessment');period_current=None
    if assessment is not None:
        try:period_current=period_assessment(company,body,assessment['terms'])==assessment
        except (AccountingError,ObjectDoesNotExist,ValueError,TypeError):period_current=False
    qualified=bool(valid and period_current and assessment['eligible_for_period_reconciliation'])
    return {'period_requires_review':bool(assessment and not freed and period_current is False),'period_assessment':assessment,'period_source_current':period_current,'line_balances':current,'allocation_totals':body.get('allocation_totals'),'schema':'sgacd-bank-group-result-v1','company_id':str(company.pk),'account_id':body['account_id'],'source_digest':body['source_digest'],'statement_id':body['statement_id'],'reconciliation_id':str(proof.pk),'review_id':proof.payload['review_id'],'group_count':len(body['groups']),'bank_row_count':len(body['bank_rows']),'ledger_line_count':len(body['ledger_lines']),'groups_confirmed':valid,'requires_review':not freed and not valid,'released':freed,'replayed':replayed,'period_reconciled':qualified,'ledger_written':False,'money_transferred':False,'bank_verified':False,'confirmations_restored':False}

@transaction.atomic
def review(company_id,*,actor,account_id,csv_text,groups,evidence_digest,expected_revision,confirmed,ledger_since=None,period=None):
    company,user=legacy._context(company_id,actor)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:raise AccountingError('Explicit first confirmation and revision required.')
    legacy.digest(evidence_digest);source=sources_locked(company,account_id,csv_text,ledger_since);selected,lines=selection(source,groups);statement=str(legacy.statement_id(company.pk,source['account_id'],source['source_digest']));old=latest(company,statement);revision=checked(old,company)['revision'] if old else 0
    if revision!=expected_revision:raise AccountingError('Grouped review changed; recover current history.')
    prior=OutboxEvent.objects.filter(event_type=APPLIED,payload__company_id=str(company.pk),payload__statement_id=statement).order_by('-payload__revision').first()
    if prior:
        origin(company,prior)
        if not released(company,prior):raise AccountingError('Release active grouped associations before reviewing again.')
    body={k:source[k] for k in ('ledger_since','company_id','account_id','source_digest','policy_revision','policy_digest','bank_rows')};body.update(statement_id=statement,groups=selected,ledger_lines=lines,reviewed_by=str(user.pk),revision=revision+1,evidence_digest=evidence_digest)
    if 'ledger_allocations' in selected[0]:
        from .bank_capacity import totals
        body['allocation_totals']=totals(selected,lines)
    if period is not None:body['period_assessment']=period_assessment(company,body,period)
    conflicts(company,body);row=OutboxEvent.objects.create(id=uuid5(NS,'review:'+statement+':'+str(revision+1)),event_type=REVIEW,domain='accounting',aggregate_root=statement,payload={'company_id':str(company.pk),'revision':revision+1,'review':body,'review_digest':fingerprint(body)},version=1)
    return {'company_id':str(company.pk),'statement_id':statement,'review_id':str(row.pk),'preview':body,'ledger_written':False,'money_transferred':False,'bank_verified':False}

@transaction.atomic
def confirm(company_id,*,actor,statement_id,review_id,confirmed):
    company,user=legacy._context(company_id,actor);row=latest(company,UUID(ident(statement_id)));body=checked(row,company)
    if confirmed is not True or str(row.pk)!=ident(review_id) or body['reviewed_by']!=str(user.pk):raise AccountingError('Second confirmation of the current review by the same owner required.')
    identifier=uuid5(NS,'applied:'+str(row.pk));existing=OutboxEvent.objects.filter(pk=identifier).first()
    if existing:return result(company,existing,True)
    if body.get('period_assessment') is not None and period_assessment(company,body,body['period_assessment']['terms'])!=body['period_assessment']:raise AccountingError('Grouped period changed after review; review balances and coverage again.')
    validate_lines(company,body,True);conflicts(company,body);payload={'company_id':str(company.pk),'statement_id':body['statement_id'],'revision':body['revision'],'review_id':str(row.pk),'review_digest':fingerprint(body)};proof=OutboxEvent(id=identifier,event_type=APPLIED,payload=payload)
    for key,value in claims(proof,body):OutboxEvent.objects.create(id=key,event_type=legacy.CLAIM,domain='accounting',aggregate_root=body['statement_id'],payload=value,version=1)
    proof=OutboxEvent.objects.create(id=identifier,event_type=APPLIED,domain='accounting',aggregate_root=body['statement_id'],payload=payload,version=1);return result(company,proof,False)

@transaction.atomic
def state(company_id,*,actor,account_id,source_digest):
    company,_=legacy._context(company_id,actor);legacy.digest(source_digest)
    from .models import Account
    if not Account.plain_objects.filter(pk=UUID(ident(account_id)),tenant=company,chart_of_accounts__tenant=company).exists():raise AccountingError('Own cash account required.')
    statement=str(legacy.statement_id(company.pk,account_id,source_digest));row=latest(company,statement);body=checked(row,company) if row else None;proof=OutboxEvent.objects.filter(event_type=APPLIED,payload__company_id=str(company.pk),payload__statement_id=statement).order_by('-payload__revision').first()
    return {'company_id':str(company.pk),'account_id':str(account_id),'source_digest':source_digest,'statement_id':statement,'revision':body['revision'] if body else 0,'review_id':str(row.pk) if row else None,'preview':body,'applied':result(company,proof,True) if proof else None,'read_only':True,'confirmations_restored':False,'ledger_written':False,'money_transferred':False,'bank_verified':False}

@transaction.atomic
def review_release(company_id,*,actor,reconciliation_id,reason_code,evidence_digest,confirmed):
    company,user=legacy._context(company_id,actor);legacy.digest(evidence_digest);proof=OutboxEvent.objects.filter(pk=UUID(ident(reconciliation_id)),event_type=APPLIED).first();origin(company,proof)
    if confirmed is not True or reason_code not in legacy.REASONS or released(company,proof):raise AccountingError('Explicit release review and supported reason required.')
    body={'company_id':str(company.pk),'reconciliation_id':str(proof.pk),'reviewed_by':str(user.pk),'reason_code':reason_code,'evidence_digest':evidence_digest,'origin_digest':fingerprint(proof.payload)};identifier=uuid5(NS,'release-review:'+fingerprint(body));row,created=OutboxEvent.objects.get_or_create(pk=identifier,defaults={'event_type':RELEASE_REVIEW,'domain':'accounting','aggregate_root':proof.payload['statement_id'],'payload':{'review':body,'review_digest':fingerprint(body)},'version':1})
    if row.event_type!=RELEASE_REVIEW or row.payload!={'review':body,'review_digest':fingerprint(body)}:raise AccountingError('Grouped release identity changed.')
    return {'company_id':str(company.pk),'reconciliation_id':str(proof.pk),'review_id':str(identifier),'ledger_written':False,'money_transferred':False,'bank_verified':False}

@transaction.atomic
def confirm_release(company_id,*,actor,review_id,confirmed):
    company,user=legacy._context(company_id,actor);row=OutboxEvent.objects.filter(pk=UUID(ident(review_id)),event_type=RELEASE_REVIEW).first();body=row.payload.get('review') if row else None
    if confirmed is not True or not isinstance(body,dict) or body.get('company_id')!=str(company.pk) or body.get('reviewed_by')!=str(user.pk) or fingerprint(body)!=row.payload.get('review_digest'):raise AccountingError('Second explicit release confirmation by the same owner required.')
    proof=OutboxEvent.objects.filter(pk=body['reconciliation_id'],event_type=APPLIED).first();origin(company,proof)
    if body['origin_digest']!=fingerprint(proof.payload):raise AccountingError('Grouped release origin changed.')
    if not released(company,proof):OutboxEvent.objects.create(id=uuid5(NS,'released:'+str(proof.pk)),event_type=RELEASED,domain='accounting',aggregate_root=proof.payload['statement_id'],payload={'review_id':str(row.pk),'review_digest':fingerprint(body)},version=1)
    return result(company,proof,True)
