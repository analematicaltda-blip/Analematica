"""Reviewed complete-period qualification across confirmed grouped bank batches.
Metadata only: source proofs and ledger are preserved; no bank authenticity claim.
"""
from uuid import UUID,uuid5
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from . import bank_grouped as groups,bank_reconciliation as legacy
from .bank_statement import cash_account
from .bank_period import assess
from .bank_capacity import totals,balances
from .invoice_intent import _money,_format_money
from .integrity import fingerprint
from .exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent

NS=UUID('c7bfbf48-9c8f-4b8b-83bb-289e15e5ef47')
REVIEW='accounting.bank-period-rollup.reviewed.v1'
APPLIED='accounting.bank-period-rollup.confirmed.v1'
FLAGS={'ledger_written':False,'money_transferred':False,'bank_verified':False,'confirmations_restored':False}
def period_id(company,account,since,until):return uuid5(NS,'period:'+str(company.pk)+':'+groups.ident(account)+':'+since+':'+until)
def latest(company,identifier):return OutboxEvent.objects.filter(event_type=REVIEW,aggregate_root=str(identifier),payload__body__company_id=str(company.pk)).order_by('-payload__body__revision').first()
def checked(company,row):
    if row is None or row.event_type!=REVIEW or row.domain!='accounting' or row.version!=1 or not isinstance(row.payload,dict) or set(row.payload)!={'body','digest'}:raise AccountingError('Period consolidation review unavailable.')
    b=row.payload['body']
    if not isinstance(b,dict) or b.get('company_id')!=str(company.pk) or type(b.get('revision')) is not int or b['revision']<1 or fingerprint(b)!=row.payload['digest'] or fingerprint(b['snapshot'])!=b.get('snapshot_digest') or b['snapshot'].get('eligible') is not True or row.pk!=uuid5(NS,'review:'+b['rollup_id']+':'+str(b['revision'])) or row.aggregate_root!=b['rollup_id'] or b['rollup_id']!=str(period_id(company,b['account_id'],b['period']['since'],b['period']['until'])):raise AccountingError('Period consolidation evidence changed.')
    return b

def snapshot(company,account_id,proof_ids,period):
    cash_account(company,account_id)
    if not isinstance(proof_ids,list) or not 1<=len(proof_ids)<=20 or len(set(proof_ids))!=len(proof_ids):raise AccountingError('One to20 unique confirmed grouped batches required.')
    ids=sorted(groups.ident(v) for v in proof_ids);bank=[];seen=set();lines={};allocated={};proofs=[]
    for identifier in ids:
        proof=OutboxEvent.objects.filter(pk=identifier,event_type=groups.APPLIED).first();body=groups.origin(company,proof)
        if body['account_id']!=account_id or groups.released(company,proof):raise AccountingError('Every batch must be active in the same cash account.')
        groups.validate_lines(company,body,True)
        proofs.append({'reconciliation_id':identifier,'statement_id':body['statement_id'],'source_digest':body['source_digest'],'review_digest':fingerprint(body),'proof_digest':fingerprint(proof.payload),'bank_row_count':len(body['bank_rows'])})
        for row in body['bank_rows']:
            if row['transaction_ref_digest'] in seen:raise AccountingError('Bank reference reused across selected batches.')
            seen.add(row['transaction_ref_digest']);bank.append({**row,'row':len(bank)+1})
            if len(bank)>200:raise AccountingError('At most200 bank rows per consolidated period.')
        amounts=body.get('allocation_totals') or totals(body['groups'],body['ledger_lines'])
        for row in body['ledger_lines']:
            key=row['ledger_line_id'];identity={k:row[k] for k in ('ledger_line_id','journal_id','journal_hash','date','direction','amount')}
            if key in lines and lines[key]!=identity:raise AccountingError('Selected batches disagree on the original cash line.')
            lines[key]=identity;allocated[key]=allocated.get(key,0)+_money(amounts[key])
            if len(lines)>200:raise AccountingError('At most200 original cash lines per consolidated period.')
    balances(company,list(lines.values())) # All active proofs, including unselected ones, must conserve capacity.
    allocations=[{'ledger_line_id':key,'original_amount':lines[key]['amount'],'allocated_amount':_format_money(allocated[key])} for key in sorted(lines)]
    complete=all(_money(r['original_amount'])==_money(r['allocated_amount']) for r in allocations)
    assessment=assess(company,account_id,period,bank,[],matched_line_ids=sorted(lines))
    return {'proofs':proofs,'allocations':allocations,'assessment':assessment,'allocations_complete':complete,'bank_row_count':len(bank),'ledger_line_count':len(lines),'eligible':complete and assessment['eligible_for_period_reconciliation']}

@transaction.atomic
def sources(company_id,*,actor,account_id):
    company,_=legacy._context(company_id,actor);cash_account(company,account_id)
    proofs=list(OutboxEvent.objects.filter(event_type=groups.APPLIED,payload__company_id=str(company.pk)).order_by('pk')[:1001])
    if len(proofs)>1000:raise AccountingError('Review archival before scanning more than1000 company batches.')
    rows=[]
    for proof in proofs:
        b=groups.origin(company,proof)
        if b['account_id']!=account_id or groups.released(company,proof):continue
        valid=True
        try:groups.validate_lines(company,b,True)
        except (AccountingError,ObjectDoesNotExist):valid=False
        days=[r['date'] for r in b['bank_rows']]
        rows.append({'reconciliation_id':str(proof.pk),'statement_id':b['statement_id'],'since':min(days),'until':max(days),'bank_row_count':len(days),'ledger_line_count':len(b['ledger_lines']),'source_current':valid})
    return {'schema':'sgacd-bank-rollup-sources-v1','company_id':str(company.pk),'account_id':account_id,'batches':rows[:50],'truncated':len(rows)>50,'limits':{'catalog':50,'selected_batches':20,'bank_rows':200,'cash_lines':200},'read_only':True,**FLAGS}

@transaction.atomic
def review(company_id,*,actor,account_id,reconciliation_ids,period,expected_revision,confirmed):
    company,user=legacy._context(company_id,actor)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:raise AccountingError('First explicit confirmation and current revision required.')
    snap=snapshot(company,account_id,reconciliation_ids,period)
    if not snap['eligible']:raise AccountingError('Complete allocations, opening/closing balances and ledger coverage required.')
    identifier=period_id(company,account_id,period['since'],period['until']);old=latest(company,identifier);revision=checked(company,old)['revision'] if old else 0
    if revision!=expected_revision:raise AccountingError('Period review changed; recover before reviewing again.')
    body={'company_id':str(company.pk),'rollup_id':str(identifier),'account_id':account_id,'period':period,'reconciliation_ids':sorted(reconciliation_ids),'reviewed_by':str(user.pk),'revision':revision+1,'snapshot':snap,'snapshot_digest':fingerprint(snap)}
    row=OutboxEvent.objects.create(id=uuid5(NS,'review:'+str(identifier)+':'+str(revision+1)),event_type=REVIEW,domain='accounting',aggregate_root=str(identifier),version=1,payload={'body':body,'digest':fingerprint(body)})
    return {'schema':'sgacd-bank-rollup-review-v1','company_id':str(company.pk),'account_id':account_id,'review_id':str(row.pk),'preview':body,'period_reconciled':False,**FLAGS}

def current(company,body):
    try:return snapshot(company,body['account_id'],body['reconciliation_ids'],body['period'])==body['snapshot']
    except (AccountingError,ObjectDoesNotExist,ValueError,TypeError,KeyError):return False

def result(company,row,proof,*,replayed):
    body=checked(company,row)
    expected={'company_id':str(company.pk),'review_id':str(row.pk),'review_digest':fingerprint(body)}
    if proof is None or proof.pk!=uuid5(NS,'confirmed:'+str(row.pk)) or proof.event_type!=APPLIED or proof.domain!='accounting' or proof.version!=1 or proof.aggregate_root!=body['rollup_id'] or proof.payload!=expected:raise AccountingError('Period consolidation confirmation evidence changed.')
    valid=current(company,body)
    return {'schema':'sgacd-bank-rollup-result-v1','company_id':str(company.pk),'account_id':body['account_id'],'review_id':str(row.pk),'confirmation_id':str(proof.pk),'revision':body['revision'],'snapshot_digest':body['snapshot_digest'],'period':body['period'],'batch_count':len(body['reconciliation_ids']),'bank_row_count':body['snapshot']['bank_row_count'],'ledger_line_count':body['snapshot']['ledger_line_count'],'source_current':valid,'requires_review':not valid,'period_reconciled':valid,'replayed':replayed,**FLAGS}

@transaction.atomic
def confirm(company_id,*,actor,review_id,confirmed):
    company,user=legacy._context(company_id,actor);row=OutboxEvent.objects.filter(pk=groups.ident(review_id)).first();body=checked(company,row)
    if confirmed is not True or body['reviewed_by']!=str(user.pk) or latest(company,body['rollup_id']).pk!=row.pk:raise AccountingError('Second confirmation by the same owner of the current review required.')
    proof=OutboxEvent.objects.filter(pk=uuid5(NS,'confirmed:'+str(row.pk))).first()
    if proof:return result(company,row,proof,replayed=True)
    if not current(company,body):raise AccountingError('Selected batches, ledger, policy or period changed after review.')
    proof=OutboxEvent.objects.create(id=uuid5(NS,'confirmed:'+str(row.pk)),event_type=APPLIED,domain='accounting',aggregate_root=body['rollup_id'],version=1,payload={'company_id':str(company.pk),'review_id':str(row.pk),'review_digest':fingerprint(body)})
    return result(company,row,proof,replayed=False)

@transaction.atomic
def state(company_id,*,actor,account_id,since,until):
    from datetime import date
    from django.utils import timezone
    company,user=legacy._context(company_id,actor);cash_account(company,account_id)
    start,end=date.fromisoformat(since),date.fromisoformat(until)
    if start.isoformat()!=since or end.isoformat()!=until or start>end or end>timezone.localdate() or (end-start).days>366:raise AccountingError('Canonical nonfuture period required.')
    row=latest(company,period_id(company,account_id,since,until));body=checked(company,row) if row else None
    proof=OutboxEvent.objects.filter(pk=uuid5(NS,'confirmed:'+str(row.pk))).first() if row else None
    return {'schema':'sgacd-bank-rollup-state-v1','company_id':str(company.pk),'account_id':account_id,'since':since,'until':until,'revision':body['revision'] if body else 0,'review_id':str(row.pk) if row else None,'preview':body,'source_current':current(company,body) if body else None,'reviewed_by_current_owner':body['reviewed_by']==str(user.pk) if body else False,'applied':result(company,row,proof,replayed=True) if proof else None,'read_only':True,**FLAGS}
