"""Reviewed first-book opening from legacy balance-sheet values, preserving source.
No invented balancing account, FX, overwrite, or rewriting of existing journals.
Authorization is enforced by the owner-scoped API; core services require actor.
"""
from datetime import date
from decimal import Decimal,localcontext
import re
from uuid import UUID,uuid5
from django.db import transaction
from django.utils import timezone
from .models import Account,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt
from .validation import lock_company,current_actor,money
from .exceptions import AccountingError
from .integrity import fingerprint
from .ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent

NS=UUID('7379d783-f281-46ec-85c4-42c41a66b81e')
REVIEW='accounting.opening.reviewed.v1'
APPLIED='accounting.opening.applied.v1'
def event_key(company):return 'opening-balance:'+str(UUID(str(company)))
def applied_id(company):return uuid5(NS,'applied:'+str(UUID(str(company))))
def latest(company):return OutboxEvent.objects.filter(event_type=REVIEW,aggregate_root=str(company),payload__company_id=str(company)).order_by('-payload__revision').first()

def source_snapshot(company_id,*,require_active=False):
    rows=list(Account.plain_objects.filter(tenant_id=company_id).exclude(initial_balance=0).select_related('chart_of_accounts').order_by('pk')[:101])
    if len(rows)>100:raise AccountingError('This bounded opening supports at most100 nonzero source accounts; larger books require a reviewed batch migration.')
    result=[]
    for row in rows:
        if (require_active and not row.is_active) or row.chart_of_accounts.tenant_id!=row.tenant_id or row.type not in {'ASSET','LIABILITY','EQUITY'}:raise AccountingError('Only active, scoped balance-sheet source accounts are supported.')
        amount=money(row.initial_balance.copy_abs())
        debit=(row.type=='ASSET')==(row.initial_balance>0)
        result.append({'account_id':str(row.pk),'type':row.type,'initial_balance':format(row.initial_balance,'.2f'),'debit':format(amount if debit else Decimal(0),'.2f'),'credit':format(amount if not debit else Decimal(0),'.2f')})
    return result

def lines_for(snapshot,company):
    return [{'account':Account.plain_objects.get(pk=row['account_id'],tenant_id=company),'debit':row['debit'],'credit':row['credit']} for row in snapshot]

def matching_existing(company_id,journal_id,snapshot,day):
    journal=JournalEntry.plain_objects.select_for_update().filter(pk=UUID(str(journal_id)),tenant_id=company_id,is_posted=True,is_reversal=False,hash_version='v2',currency='COP',base_currency='COP',exchange_rate=Decimal('1')).first()
    if journal is None or journal.date!=day or journal.compute_hash()!=journal.system_hash or JournalEntry.plain_objects.filter(tenant_id=company_id,is_posted=True,reversed_entry_id=journal.pk).exists():raise AccountingError('Existing opening must be intact, unreversed, scoped and match the reviewed date.')
    if JournalEntry.plain_objects.filter(tenant_id=company_id,is_posted=True,date__lt=day).exists():raise AccountingError('An existing opening must precede other economic dates.')
    actual=list(LedgerEntry.plain_objects.filter(journal_entry=journal).select_related('account').order_by('account_id'));expected=sorted(snapshot,key=lambda r:r['account_id'])
    if len(actual)!=len(expected) or any(line.tenant_id!=journal.tenant_id or line.account.tenant_id!=journal.tenant_id or line.currency!='COP' or line.amount_transaction!=line.debit_amount+line.credit_amount or line.amount_base!=line.debit_amount+line.credit_amount or str(line.account_id)!=row['account_id'] or line.debit_amount!=Decimal(row['debit']) or line.credit_amount!=Decimal(row['credit']) for line,row in zip(actual,expected)):raise AccountingError('The existing journal does not exactly match the preserved opening source.')
    return journal

def inspect_opening(company_id,cutoff=None):
    """Validate preserved source against reviewed, immutable opening journal.

    Called even if source values have all been reset to zero: hiding a changed
    snapshot must not bypass the reconciliation guard. No repairs are performed.
    """
    company_id=UUID(str(company_id))
    snapshot=source_snapshot(company_id)
    proof=OutboxEvent.objects.filter(pk=applied_id(company_id),event_type=APPLIED,payload__company_id=str(company_id)).first()
    if proof is None:
        if snapshot:raise AccountingError('Legacy initial balances require a reviewed opening before reporting.')
        return None
    p=proof.payload
    review=OutboxEvent.objects.filter(pk=p.get('review_id'),event_type=REVIEW,payload__company_id=str(company_id)).first()
    body=review.payload.get('review') if review else None
    if not isinstance(body,dict) or fingerprint(body)!=p.get('review_digest') or fingerprint(snapshot)!=p.get('source_digest') or body.get('snapshot')!=snapshot:raise AccountingError('Opening source or review evidence changed.')
    journal=JournalEntry.plain_objects.filter(pk=p.get('journal_id'),tenant_id=company_id,is_posted=True,is_reversal=False,hash_version='v2',currency='COP',base_currency='COP',exchange_rate=Decimal('1')).first()
    receipt=AccountingEventReceipt.objects.filter(tenant_id=company_id,event_id=event_key(company_id)).first() if p.get('mode','POST_NEW')=='POST_NEW' else None
    if p.get('mode','POST_NEW')!=body.get('mode','POST_NEW'):raise AccountingError('Opening origin mode mismatch.')
    if p.get('mode')=='LINK_EXISTING' and body.get('existing_journal_id')!=p.get('journal_id'):raise AccountingError('Opening link identity mismatch.')
    if journal is None or (p.get('mode','POST_NEW')=='POST_NEW' and (receipt is None or receipt.journal_id!=journal.pk)) or journal.compute_hash()!=p.get('journal_hash') or journal.system_hash!=p.get('journal_hash'):raise AccountingError('Opening journal evidence requires reconciliation.')
    if cutoff is not None and journal.date>cutoff:raise AccountingError('No qualified report is available before the reviewed opening date.')
    actual=list(LedgerEntry.plain_objects.filter(journal_entry=journal).order_by('account_id'))
    expected=sorted(snapshot,key=lambda row:row['account_id'])
    if len(actual)!=len(expected) or any(line.tenant_id!=journal.tenant_id or line.currency!='COP' or line.amount_transaction!=line.debit_amount+line.credit_amount or line.amount_base!=line.debit_amount+line.credit_amount or str(line.account_id)!=row['account_id'] or line.debit_amount!=Decimal(row['debit']) or line.credit_amount!=Decimal(row['credit']) for line,row in zip(actual,expected)):raise AccountingError('Opening lines differ from the reviewed source.')
    reversals=list(JournalEntry.plain_objects.filter(tenant_id=company_id,is_posted=True,reversed_entry_id=journal.pk)[:2])
    if len(reversals)>1:raise AccountingError('Multiple opening reversals require reconciliation.')
    if reversals:
        reverse=reversals[0];contra=list(LedgerEntry.plain_objects.filter(journal_entry=reverse,tenant_id=company_id).order_by('account_id'))
        if reverse.compute_hash()!=reverse.system_hash or len(contra)!=len(actual) or any(c.account_id!=a.account_id or c.debit_amount!=a.credit_amount or c.credit_amount!=a.debit_amount for c,a in zip(contra,actual)):raise AccountingError('Opening reversal requires reconciliation.')
    return {'journal_id':str(journal.pk),'source_digest':p['source_digest'],'reversed':bool(reversals),'source_fields_preserved':True}

@transaction.atomic
def review_opening(company_id,*,actor,entry_date,evidence_digest,expected_revision,confirmed,existing_journal_id=None):
    company=lock_company(company_id);user=current_actor(actor)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0 or not isinstance(evidence_digest,str) or not re.fullmatch('[0-9a-f]{64}',evidence_digest):raise AccountingError('Explicit opening review and evidence required.')
    day=date.fromisoformat(entry_date)
    if day.isoformat()!=entry_date or day>timezone.localdate() or company.currency!='COP':raise AccountingError('Valid COP economic date required; no implicit FX.')
    if OutboxEvent.objects.filter(pk=applied_id(company.pk)).exists():raise AccountingError('Opening is already reconciled; no overwrite.')
    if existing_journal_id is None and JournalEntry.plain_objects.filter(tenant=company,is_posted=True).exists():raise AccountingError('Existing books require an explicitly reviewed matching journal; no duplicate opening.')
    snapshot=source_snapshot(company.pk,require_active=existing_journal_id is None)
    if len(snapshot)<2:raise AccountingError('At least two nonzero source accounts are required.')
    with localcontext() as ctx:
        ctx.prec=38
        debit=sum((Decimal(r['debit']) for r in snapshot),Decimal(0));credit=sum((Decimal(r['credit']) for r in snapshot),Decimal(0))
    if debit!=credit:raise AccountingError('Source balances do not balance; no balancing account is invented.')
    existing=matching_existing(company.pk,existing_journal_id,snapshot,day) if existing_journal_id is not None else None
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=day,period_end__gte=day)[:2]) if existing is None else [existing.period]
    if len(periods)!=1:raise AccountingError('Exactly one open period must contain a new opening date.')
    old=latest(company.pk);previous=old.payload['revision'] if old else 0
    if previous!=expected_revision:raise AccountingError('Opening review changed; reload.')
    body={'company_id':str(company.pk),'reviewed_by':str(user.pk),'entry_date':entry_date,'period_id':str(periods[0].pk),'currency':'COP','snapshot':snapshot,'source_digest':fingerprint(snapshot),'evidence_digest':evidence_digest,'revision':previous+1,'total_debit':format(debit,'.2f'),'total_credit':format(credit,'.2f'),'independently_verified':False,'mode':'LINK_EXISTING' if existing else 'POST_NEW','existing_journal_id':str(existing.pk) if existing else None,'existing_journal_hash':existing.system_hash if existing else None}
    row=OutboxEvent.objects.create(id=uuid5(NS,'review:'+str(company.pk)+':'+str(previous+1)),event_type=REVIEW,domain='accounting',aggregate_root=str(company.pk),payload={'company_id':str(company.pk),'revision':previous+1,'review':body,'review_digest':fingerprint(body)},version=1)
    return {'company_id':str(company.pk),'review_id':str(row.pk),'preview':body,'ledger_written':False}

@transaction.atomic
def apply_opening(company_id,*,actor,review_id,confirmed):
    company=lock_company(company_id);user=current_actor(actor)
    if confirmed is not True:raise AccountingError('Second opening confirmation required.')
    review=latest(company.pk)
    if review is None or str(review.pk)!=str(UUID(str(review_id))):raise AccountingError('Current opening review required.')
    p=review.payload['review'];snapshot=source_snapshot(company.pk)
    if fingerprint(p)!=review.payload['review_digest'] or p['reviewed_by']!=str(user.pk) or p['snapshot']!=snapshot or company.currency!='COP':raise AccountingError('Owner, source, currency or review changed.')
    proof=OutboxEvent.objects.filter(pk=applied_id(company.pk)).first()
    if proof:
        if proof.payload.get('review_id')!=str(review.pk):raise AccountingError('Opening origin conflicts with this review.')
        resolution=inspect_opening(company.pk)
        linked=p.get('mode')=='LINK_EXISTING'
        return {'company_id':str(company.pk),'journal_id':resolution['journal_id'],'replayed':True,'ledger_written':not linked,'linked_existing':linked,'metadata_recorded':True,'source_fields_preserved':True,'reversed':resolution['reversed'],'money_transferred':False}
    if p.get('mode')=='LINK_EXISTING':
        journal=matching_existing(company.pk,p['existing_journal_id'],snapshot,date.fromisoformat(p['entry_date']))
        if journal.system_hash!=p['existing_journal_hash']:raise AccountingError('The existing journal changed after review.')
        OutboxEvent.objects.create(id=applied_id(company.pk),event_type=APPLIED,domain='accounting',aggregate_root=str(company.pk),payload={'company_id':str(company.pk),'review_id':str(review.pk),'review_digest':fingerprint(p),'source_digest':fingerprint(snapshot),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'mode':'LINK_EXISTING'},version=1)
        return {'company_id':str(company.pk),'journal_id':str(journal.pk),'replayed':False,'ledger_written':False,'linked_existing':True,'metadata_recorded':True,'source_fields_preserved':True,'reversed':False,'money_transferred':False}
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=event_key(company.pk)).first()
    if receipt:
        evidence=inspect_opening(company.pk)
        if evidence is None:raise AccountingError('Missing opening origin proof; history is not reconstructed.')
        return {'company_id':str(company.pk),'journal_id':str(receipt.journal_id),'replayed':True,'ledger_written':True,'source_fields_preserved':True,'reversed':evidence['reversed'],'money_transferred':False}
    if JournalEntry.plain_objects.filter(tenant=company,is_posted=True).exists() or OutboxEvent.objects.filter(pk=applied_id(company.pk)).exists():raise AccountingError('Existing books or conflicting origin evidence require reconciliation.')
    journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=date.fromisoformat(p['entry_date']),description='Reviewed first-book opening',lines_data=lines_for(snapshot,company.pk),actor=user,idempotency_key=event_key(company.pk),period_id=p['period_id'])
    OutboxEvent.objects.create(id=applied_id(company.pk),event_type=APPLIED,domain='accounting',aggregate_root=str(company.pk),payload={'company_id':str(company.pk),'review_id':str(review.pk),'review_digest':fingerprint(p),'source_digest':fingerprint(snapshot),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'mode':'POST_NEW'},version=1)
    return {'company_id':str(company.pk),'journal_id':str(journal.pk),'replayed':False,'ledger_written':True,'linked_existing':False,'metadata_recorded':True,'source_fields_preserved':True,'reversed':False,'money_transferred':False}

@transaction.atomic
def opening_state(company_id,*,actor):
    company=lock_company(company_id);user=current_actor(actor);snapshot=source_snapshot(company.pk);row=latest(company.pk)
    review=None
    if row:
        body=row.payload.get('review')
        if not isinstance(body,dict) or fingerprint(body)!=row.payload.get('review_digest'):raise AccountingError('Opening review evidence changed.')
        review={'review_id':str(row.pk),'preview':body,'source_matches':body['snapshot']==snapshot,'reviewed_by_current_owner':body['reviewed_by']==str(user.pk),'ledger_written':False}
    proof=OutboxEvent.objects.filter(pk=applied_id(company.pk)).first();applied=inspect_opening(company.pk) if proof else None
    display={str(a.pk):a for a in Account.plain_objects.filter(tenant=company,pk__in=[r['account_id'] for r in snapshot])}
    return {'company_id':str(company.pk),'read_only':True,'source':[dict(r,code=display[r['account_id']].code,name=display[r['account_id']].name) for r in snapshot],'review':review,'applied':applied,'revision':row.payload['revision'] if row else 0,'can_review_first_book':company.currency=='COP' and len(snapshot)>=2 and not Account.plain_objects.filter(tenant=company,pk__in=[r['account_id'] for r in snapshot],is_active=False).exists() and not JournalEntry.plain_objects.filter(tenant=company,is_posted=True).exists() and proof is None,'source_fields_preserved':True,'confirmations_restored':False}
