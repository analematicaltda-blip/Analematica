"""Paged, preserved legacy source -> one reviewed first-book COP journal.
Chunks qualify evidence only; partial opening journals are never committed.
"""
from contextvars import ContextVar
from datetime import date
from decimal import Decimal,localcontext
from uuid import UUID,uuid5
from django.db import transaction
from django.utils import timezone
from . import opening_balances as old
from .models import Account,JournalEntry,LedgerEntry,FiscalPeriod,AccountingEventReceipt
from .validation import lock_company,current_actor,money
from .integrity import fingerprint
from .exceptions import AccountingError
from apps.core_erp.outbox_models import OutboxEvent
NS=UUID('95b510fe-6c77-4a09-8bf5-322bc9c3ac79')
REVIEW='accounting.opening-chunks.reviewed.v1'
CHUNK='accounting.opening-chunks.source.v1'
APPLIED='accounting.opening-chunks.applied.v1'
PREFIX='opening-chunks:'
DESCRIPTION='Reviewed first-book opening from preserved source chunks'
LIMIT=250
PAGE=50
_authorized=ContextVar('chunked_opening_authorized',default=None)
def key(kind,company,value):return uuid5(NS,kind+':'+str(company)+':'+str(value))
def authorize(company,actor,event):
    if _authorized.get()!=(str(company),str(actor),event):raise AccountingError('Chunked opening requires its explicit reviewed command.')
def context(company_id,actor):
    company=lock_company(company_id);user=current_actor(actor)
    if company.currency!='COP' or getattr(user,'is_agent',False):raise AccountingError('Personal reviewer of COP first books required.')
    return company,user

def live(company,*,active=True):
    accounts=list(Account.plain_objects.select_for_update().filter(tenant=company).exclude(initial_balance=0).select_related('chart_of_accounts').order_by('pk')[:LIMIT+1])
    if len(accounts)>LIMIT:raise AccountingError('At most250 preserved nonzero accounts; larger migrations need a separately reviewed contract.')
    rows=[]
    for a in accounts:
        if a.chart_of_accounts.tenant_id!=company.pk or a.type not in {'ASSET','LIABILITY','EQUITY'} or active and not a.is_active:raise AccountingError('Scoped balance-sheet source accounts required; no income/expense migration inference.')
        amount=money(abs(a.initial_balance));debit=(a.type=='ASSET')==(a.initial_balance>0)
        rows.append({'account_id':str(a.pk),'code':a.code,'type':a.type,'initial_balance':format(a.initial_balance,'.2f'),'debit':format(amount if debit else Decimal(0),'.2f'),'credit':format(amount if not debit else Decimal(0),'.2f')})
    pages=[rows[i:i+PAGE] for i in range(0,len(rows),PAGE)]
    with localcontext() as ctx:
        ctx.prec=38;left=sum((Decimal(r['debit']) for r in rows),Decimal(0));right=sum((Decimal(r['credit']) for r in rows),Decimal(0))
    return {'rows':rows,'pages':pages,'source_root_digest':fingerprint([fingerprint(p) for p in pages]),'account_count':len(rows),'chunk_count':len(pages),'total_debit':format(left,'.2f'),'total_credit':format(right,'.2f')}

def latest(company):return OutboxEvent.objects.filter(event_type=REVIEW,aggregate_root=str(company.pk),payload__body__company_id=str(company.pk)).order_by('-payload__body__revision').first()

def history_guard(company,row):
    if row is None and OutboxEvent.objects.filter(event_type=CHUNK,payload__company_id=str(company.pk)).exists():raise AccountingError('Opening chunks exist without their manifest; no automatic reconstruction.')

def checked(company,row):
    if row is None or row.event_type!=REVIEW or row.domain!='accounting' or row.version!=1 or row.aggregate_root!=str(company.pk) or not isinstance(row.payload,dict) or set(row.payload)!={'body','digest'}:raise AccountingError('Preserved chunked opening review unavailable.')
    b=row.payload['body']
    if not isinstance(b,dict) or b.get('company_id')!=str(company.pk) or type(b.get('revision')) is not int or b['revision']<1 or row.pk!=key('review',company.pk,b['revision']) or fingerprint(b)!=row.payload['digest'] or not 2<=b['account_count']<=LIMIT or type(b['account_count']) is not int or type(b['chunk_count']) is not int or b['chunk_count']!=(b['account_count']+PAGE-1)//PAGE:raise AccountingError('Opening manifest changed.')
    chunks=list(OutboxEvent.objects.filter(event_type=CHUNK,aggregate_root=str(row.pk)).order_by('payload__index')[:7]);rows=[];digests=[]
    if len(chunks)!=b['chunk_count']:raise AccountingError('Opening source chunk missing or duplicated.')
    for index,c in enumerate(chunks):
        p=c.payload;records=p.get('rows') if isinstance(p,dict) else None
        if c.pk!=key('chunk',row.pk,index) or c.domain!='accounting' or c.version!=1 or not isinstance(records,list) or not 1<=len(records)<=PAGE or p!={'company_id':str(company.pk),'review_id':str(row.pk),'index':index,'rows':records,'digest':fingerprint(records)} or (index<b['chunk_count']-1 and len(records)!=PAGE):raise AccountingError('Opening source chunk changed.')
        rows.extend(records);digests.append(p['digest'])
    ids=[r['account_id'] for r in rows]
    if len(rows)!=b['account_count'] or ids!=sorted(set(ids)) or fingerprint(digests)!=b['source_root_digest']:raise AccountingError('Opening root/count/order changed.')
    with localcontext() as ctx:
        ctx.prec=38;debit=sum((Decimal(r['debit']) for r in rows),Decimal(0));credit=sum((Decimal(r['credit']) for r in rows),Decimal(0))
    if format(debit,'.2f')!=b['total_debit'] or format(credit,'.2f')!=b['total_credit'] or debit!=credit or debit<=0:raise AccountingError('Opening chunks do not balance; no balancing account is invented.')
    return b,rows

@transaction.atomic
def sources(company_id,*,actor,after_id=None):
    company,_=context(company_id,actor);s=live(company,active=False)
    if after_id is not None and (not isinstance(after_id,str) or str(UUID(after_id))!=after_id):raise AccountingError('Canonical source cursor required.')
    ids=[r['account_id'] for r in s['rows']]
    if after_id is not None and after_id not in ids:raise AccountingError('Cursor no longer belongs to the preserved source.')
    offset=ids.index(after_id)+1 if after_id else 0;page=s['rows'][offset:offset+PAGE];display={str(a.pk):a for a in Account.plain_objects.filter(tenant=company,pk__in=[r['account_id'] for r in page])};review=latest(company);history_guard(company,review)
    return {'schema':'sgacd-opening-chunks-sources-v1','business_date':timezone.localdate().isoformat(),'company_id':str(company.pk),'source_root_digest':s['source_root_digest'],'account_count':s['account_count'],'chunk_count':s['chunk_count'],'total_debit':s['total_debit'],'total_credit':s['total_credit'],'rows':[{**r,'code':display[r['account_id']].code,'name':display[r['account_id']].name,'name_digest':fingerprint(display[r['account_id']].name),'active':display[r['account_id']].is_active} for r in page],'next_after':page[-1]['account_id'] if offset+len(page)<len(ids) else None,'revision':checked(company,review)[0]['revision'] if review else 0,'can_review':not OutboxEvent.objects.filter(pk=old.applied_id(company.pk)).exists() and not JournalEntry.plain_objects.filter(tenant=company,is_posted=True).exists(),'limits':{'accounts':LIMIT,'page':PAGE},'read_only':True,'ledger_written':False,'money_transferred':False,'source_fields_preserved':True,'source_independently_verified':False,'confirmations_restored':False}

@transaction.atomic
def review(company_id,*,actor,entry_date,evidence_digest,source_root_digest,expected_revision,confirmed):
    company,user=context(company_id,actor)
    from .bank_reconciliation import digest
    digest(evidence_digest);digest(source_root_digest)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:raise AccountingError('Explicit first confirmation and expected revision required.')
    day=date.fromisoformat(entry_date)
    if day.isoformat()!=entry_date or day>timezone.localdate():raise AccountingError('Canonical nonfuture opening date required.')
    if OutboxEvent.objects.filter(pk=old.applied_id(company.pk)).exists() or JournalEntry.plain_objects.filter(tenant=company,is_posted=True).exists():raise AccountingError('Only first books without an existing opening or posted journals; no duplicate or overwrite.')
    s=live(company)
    if s['source_root_digest']!=source_root_digest or s['account_count']<2 or s['total_debit']!=s['total_credit']:raise AccountingError('Preserved source changed, is empty or does not balance.')
    previous=latest(company);history_guard(company,previous);revision=checked(company,previous)[0]['revision'] if previous else 0
    if expected_revision!=revision:raise AccountingError('Opening review changed; recover current revision.')
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=day,period_end__gte=day)[:2])
    if len(periods)!=1:raise AccountingError('Exactly one open opening period required.')
    b={'company_id':str(company.pk),'reviewed_by':str(user.pk),'entry_date':entry_date,'period_id':str(periods[0].pk),'revision':revision+1,'source_root_digest':source_root_digest,'account_count':s['account_count'],'chunk_count':s['chunk_count'],'total_debit':s['total_debit'],'total_credit':s['total_credit'],'evidence_digest':evidence_digest,'mode':'CHUNKED_SOURCE','source_independently_verified':False}
    row=OutboxEvent.objects.create(id=key('review',company.pk,revision+1),event_type=REVIEW,domain='accounting',aggregate_root=str(company.pk),version=1,payload={'body':b,'digest':fingerprint(b)})
    for index,records in enumerate(s['pages']):OutboxEvent.objects.create(id=key('chunk',row.pk,index),event_type=CHUNK,domain='accounting',aggregate_root=str(row.pk),version=1,payload={'company_id':str(company.pk),'review_id':str(row.pk),'index':index,'rows':records,'digest':fingerprint(records)})
    checked(company,row)
    return {'schema':'sgacd-opening-chunks-review-v1','company_id':str(company.pk),'review_id':str(row.pk),'preview':b,'ledger_written':False,'money_transferred':False,'source_fields_preserved':True,'source_independently_verified':False}

def origin(company,marker,cutoff=None):
    if marker is None or marker.event_type!=APPLIED or marker.domain!='accounting' or marker.version!=1 or marker.pk!=old.applied_id(company.pk) or marker.aggregate_root!=str(company.pk) or not isinstance(marker.payload,dict):raise AccountingError('Chunked opening origin unavailable.')
    p=marker.payload;row=OutboxEvent.objects.filter(pk=p.get('review_id')).first();b,records=checked(company,row);source=live(company,active=False)
    journal=JournalEntry.plain_objects.filter(pk=p.get('journal_id'),tenant=company,is_posted=True,is_reversal=False).first()
    expected={'company_id':str(company.pk),'review_id':str(row.pk),'review_digest':fingerprint(b),'source_root_digest':b['source_root_digest'],'journal_id':str(journal.pk) if journal else None,'journal_hash':journal.system_hash if journal else None}
    if p!=expected or source['rows']!=records or source['source_root_digest']!=b['source_root_digest'] or journal is None or journal.hash_version!='v2' or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=1 or journal.date.isoformat()!=b['entry_date'] or str(journal.period_id)!=b['period_id'] or str(journal.created_by_id)!=b['reviewed_by'] or journal.financial_event_id!=PREFIX+str(row.pk) or journal.compute_hash()!=journal.system_hash:raise AccountingError('Preserved opening source or posted journal changed.')
    if cutoff is not None and journal.date>cutoff:raise AccountingError('No report is qualified before the preserved opening date.')
    lines=list(LedgerEntry.plain_objects.filter(journal_entry=journal).order_by('account_id'))
    if len(lines)!=len(records) or any(l.tenant_id!=company.pk or l.currency!='COP' or l.amount_base!=l.debit_amount+l.credit_amount or l.amount_transaction!=l.amount_base or str(l.account_id)!=r['account_id'] or format(l.debit_amount,'.2f')!=r['debit'] or format(l.credit_amount,'.2f')!=r['credit'] for l,r in zip(lines,records)):raise AccountingError('Chunked opening lines differ from preserved source.')
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=PREFIX+str(row.pk),journal=journal).first()
    contract={'schema':'manual-journal-v2','tenant_id':str(company.pk),'actor_id':journal.created_by_id,'date':b['entry_date'],'description':DESCRIPTION,'period_id':b['period_id'],'lines':[{'account':r['account_id'],'debit':r['debit'],'credit':r['credit']} for r in records]}
    if receipt is None or receipt.payload_hash!=fingerprint(contract):raise AccountingError('Chunked opening posting receipt changed.')
    reversals=list(JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id=journal.pk)[:2])
    if len(reversals)>1:raise AccountingError('Conflicting opening reversals require reconciliation.')
    if reversals:
        from .ledger_engine import historical_reversal_valuation
        reverse=reversals[0];historical_reversal_valuation(reverse,list(LedgerEntry.plain_objects.filter(journal_entry=reverse).select_related('account')))
        if reverse.compute_hash()!=reverse.system_hash:raise AccountingError('Opening reversal integrity changed.')
    return row,b,journal,bool(reversals)

def verify_posted_origin(company,journal):
    result=origin(company,OutboxEvent.objects.filter(pk=old.applied_id(company.pk)).first())
    if result[2].pk!=journal.pk or journal.financial_event_id!=PREFIX+str(result[0].pk):raise AccountingError('A different journal cannot borrow the preserved opening origin.')
    return result

@transaction.atomic
def inspect(company,cutoff=None):
    company=lock_company(company.pk)
    row,b,journal,reversed=origin(company,OutboxEvent.objects.filter(pk=old.applied_id(company.pk)).first(),cutoff)
    return {'journal_id':str(journal.pk),'source_digest':b['source_root_digest'],'reversed':reversed,'source_fields_preserved':True,'opening_mode':'CHUNKED_SOURCE','account_count':b['account_count'],'chunk_count':b['chunk_count']}

def result(company,row,marker,replayed):
    found,b,journal,reversed=origin(company,marker)
    if found.pk!=row.pk:raise AccountingError('Opening belongs to a different review.')
    return {'schema':'sgacd-opening-chunks-result-v1','company_id':str(company.pk),'review_id':str(row.pk),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'source_root_digest':b['source_root_digest'],'account_count':b['account_count'],'chunk_count':b['chunk_count'],'total_debit':b['total_debit'],'total_credit':b['total_credit'],'reversed':reversed,'replayed':replayed,'ledger_written':True,'money_transferred':False,'source_fields_preserved':True,'source_independently_verified':False}

@transaction.atomic
def apply(company_id,*,actor,review_id,confirmed):
    company,user=context(company_id,actor);row=latest(company);b,records=checked(company,row)
    if confirmed is not True or str(row.pk)!=str(UUID(review_id)) or b['reviewed_by']!=str(user.pk):raise AccountingError('Second confirmation of current opening by the same reviewer required.')
    marker=OutboxEvent.objects.filter(pk=old.applied_id(company.pk)).first()
    if marker:return result(company,row,marker,True)
    if live(company)['rows']!=records or JournalEntry.plain_objects.filter(tenant=company,is_posted=True).exists():raise AccountingError('Opening source or first-book state changed after review.')
    event=PREFIX+str(row.pk)
    if AccountingEventReceipt.objects.filter(tenant=company,event_id=event).exists() or JournalEntry.plain_objects.filter(tenant=company,financial_event_id=event).exists():raise AccountingError('Opening origin conflict; no reconstruction.')
    accounts={str(a.pk):a for a in Account.plain_objects.filter(tenant=company,pk__in=[r['account_id'] for r in records])}
    lines=[{'account':accounts[r['account_id']],'debit':r['debit'],'credit':r['credit']} for r in records]
    from .ledger_engine import LedgerEngine
    token=_authorized.set((str(company.pk),str(user.pk),event))
    try:journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=date.fromisoformat(b['entry_date']),description=DESCRIPTION,lines_data=lines,actor=user,idempotency_key=event,period_id=b['period_id'])
    finally:_authorized.reset(token)
    marker=OutboxEvent.objects.create(id=old.applied_id(company.pk),event_type=APPLIED,domain='accounting',aggregate_root=str(company.pk),version=1,payload={'company_id':str(company.pk),'review_id':str(row.pk),'review_digest':fingerprint(b),'source_root_digest':b['source_root_digest'],'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    return result(company,row,marker,False)

@transaction.atomic
def state(company_id,*,actor):
    company,user=context(company_id,actor);row=latest(company);history_guard(company,row);b,records=checked(company,row) if row else (None,[]);marker=OutboxEvent.objects.filter(pk=old.applied_id(company.pk)).first()
    current=live(company,active=False)
    if marker is not None and marker.event_type!=APPLIED:raise AccountingError('Existing opening belongs to the preserved original workflow.')
    return {'schema':'sgacd-opening-chunks-state-v1','company_id':str(company.pk),'revision':b['revision'] if b else 0,'review_id':str(row.pk) if row else None,'preview':b,'source_current':(current['rows']==records and (marker is not None or not Account.plain_objects.filter(tenant=company,pk__in=[r['account_id'] for r in records],is_active=False).exists())) if b else None,'reviewed_by_current_owner':b['reviewed_by']==str(user.pk) if b else False,'applied':result(company,row,marker,True) if marker else None,'read_only':True,'ledger_written':False,'money_transferred':False,'source_fields_preserved':True,'source_independently_verified':False,'confirmations_restored':False}

def compatibility_state(company,user):
    s=live(company,active=False);row=latest(company);history_guard(company,row);b,_=checked(company,row) if row else (None,[]);marker=OutboxEvent.objects.filter(pk=old.applied_id(company.pk)).first();applied=inspect(company) if marker else None
    display={str(a.pk):a for a in Account.plain_objects.filter(tenant=company,pk__in=[r['account_id'] for r in s['rows']])}
    return {'company_id':str(company.pk),'read_only':True,'source':[{**r,'code':display[r['account_id']].code,'name':display[r['account_id']].name} for r in s['rows']],'review':None,'applied':applied,'revision':b['revision'] if b else 0,'can_review_first_book':False,'source_fields_preserved':True,'confirmations_restored':False,'opening_mode':'CHUNKED_SOURCE'}
