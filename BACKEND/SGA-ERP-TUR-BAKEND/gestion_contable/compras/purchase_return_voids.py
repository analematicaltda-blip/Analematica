"""Two owner confirmations to counter the most recent active return, append-only.
Never deletes its source, releases document evidence, pays cash or issues DIAN notes.
"""
from datetime import date,timedelta
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.exceptions import AccountingError
from . import purchase_returns as returns
from .purchase_returns import OutboxEvent,JournalEntry,LedgerEntry,AccountingEventReceipt,Account,FiscalPeriod,LedgerEngine

REASONS={'DATA_ENTRY_ERROR','DUPLICATE_RETURN','SOURCE_WITHDRAWN'}

def opposite(lines):return [{**r,'debit':r['credit'],'credit':r['debit']} for r in lines]

def validate_proof(company,proof,original,source,target_proof,target_review):
    p=returns.read(proof,returns.VOIDED,company);r=returns.read(OutboxEvent.objects.filter(pk=p['review_id']).first(),returns.VOID_REVIEW,company);target=returns.read(target_proof,returns.POSTED,company)
    if p['review_digest']!=fingerprint(r) or p['return_id']!=target['return_id'] or p['return_id']!=r['return_id'] or p['invoice_id']!=target['invoice_id'] or p['invoice_id']!=r['invoice_id'] or p['revision']!=r['revision'] or p['void_index']!=r['void_index'] or p['original_journal_id']!=source['journal_id'] or p['target_journal_id']!=target['journal_id'] or r['target_journal_id']!=target['journal_id'] or r['target_proof_digest']!=target_proof.payload['digest'] or r['document_id']!=original['document_id'] or r['lines']!=opposite(target_review['lines']) or r['totals']!=target_review['totals'] or r['reason_code'] not in REASONS:raise AccountingError('Correction source or contra lines changed.')
    journal=JournalEntry.plain_objects.filter(pk=p['journal_id'],tenant=company,is_posted=True,is_reversal=False).first()
    if journal is None or journal.financial_event_id!=returns.event_key(source['journal_id'],'void:'+p['return_id']) or journal.system_hash!=p['journal_hash'] or journal.compute_hash()!=p['journal_hash'] or journal.date.isoformat()!=r['entry_date'] or str(journal.period_id)!=r['period_id'] or str(journal.created_by_id)!=r['reviewed_by'] or JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id=journal.pk).exists():raise AccountingError('Correction journal changed.')
    actual=sorted((str(line.account_id),format(line.debit_amount,'.2f'),format(line.credit_amount,'.2f')) for line in LedgerEntry.plain_objects.filter(tenant=company,journal_entry=journal))
    if actual!=sorted((line['account_id'],line['debit'],line['credit']) for line in r['lines']):raise AccountingError('Correction lines changed.')
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=journal.financial_event_id,journal=journal).first();contract={'schema':'manual-journal-v2','tenant_id':str(company.pk),'actor_id':journal.created_by_id,'date':r['entry_date'],'description':'Reviewed native return correction','period_id':r['period_id'],'lines':[{'account':line['account_id'],'debit':line['debit'],'credit':line['credit']} for line in r['lines']]}
    if receipt is None or receipt.payload_hash!=fingerprint(contract):raise AccountingError('Correction receipt changed.')
    return r

def active_target(entries,return_id):
    active=[row for row in entries if not row.get('reversed')]
    if not active or active[-1]['return_id']!=return_id:raise AccountingError('Correct the latest active return first; no rounding reallocation.')
    return active[-1]

@transaction.atomic
def review(*,actor,provider_id,invoice_id,return_id,request_id,entry_date,reason_code,evidence_digest,expected_revision,confirmed):
    user,provider,company,_,body,source,entries,used,head=returns.context(actor,provider_id,invoice_id);returns.ledger.identifier(return_id);returns.ledger.identifier(request_id);returns.ledger.digest(evidence_digest);target=active_target(entries,return_id)
    if confirmed is not True or type(expected_revision) is not int or expected_revision!=len(entries) or reason_code not in REASONS:raise AccountingError('Explicit first confirmation, reason and current revision required.')
    target_proof=OutboxEvent.objects.filter(pk=returns.key(returns.POSTED,company.pk,invoice_id,return_id)).first();target_body=returns.read(target_proof,returns.POSTED,company);original_review=returns.read(OutboxEvent.objects.filter(pk=target_body['review_id']).first(),returns.REVIEW,company);day=date.fromisoformat(entry_date)
    if day.isoformat()!=entry_date or entry_date<original_review['entry_date'] or day>timezone.localdate():raise AccountingError('Canonical nonfuture correction date not before its source required.')
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=day,period_end__gte=day)[:2])
    if len(periods)!=1:raise AccountingError('Unique open correction period required.')
    content={'company_id':str(company.pk),'provider_id':str(provider.pk),'invoice_id':invoice_id,'document_id':body['document_id'],'return_id':return_id,'request_id':request_id,'revision':len(entries),'void_index':sum(bool(e.get('reversed')) for e in entries)+1,'history_digest':head,'original_journal_id':source['journal_id'],'target_journal_id':target['journal_id'],'target_proof_digest':target_proof.payload['digest'],'reviewed_by':str(user.pk),'entry_date':entry_date,'period_id':str(periods[0].pk),'reason_code':reason_code,'evidence_digest':evidence_digest,'totals':original_review['totals'],'lines':opposite(original_review['lines'])}
    old=OutboxEvent.objects.filter(pk=returns.key(returns.VOID_REVIEW,company.pk,invoice_id,request_id)).first()
    if old:
        saved=returns.read(old,returns.VOID_REVIEW,company)
        if {k:v for k,v in saved.items() if k!='expires_at'}!=content:raise AccountingError('Correction request already bound to different source.')
        content=saved
    else:content['expires_at']=(timezone.now()+timedelta(minutes=15)).isoformat();old=returns.store(returns.VOID_REVIEW,company,content)
    return {'company_id':str(company.pk),'invoice_id':invoice_id,'return_id':return_id,'review_id':str(old.pk),'preview':content,'ledger_written':False,'money_transferred':False,'fiscal_document_created':False,'regulatory_verified':False}

@transaction.atomic
def post(*,actor,provider_id,invoice_id,review_id,confirmed):
    user,provider,company,_,body,source,entries,used,head=returns.context(actor,provider_id,invoice_id);returns.ledger.identifier(review_id);review=OutboxEvent.objects.filter(pk=review_id).first();r=returns.read(review,returns.VOID_REVIEW,company)
    if confirmed is not True or r['reviewed_by']!=str(user.pk) or r['invoice_id']!=invoice_id or r['provider_id']!=str(provider.pk):raise AccountingError('Second explicit confirmation by same owner required.')
    old=next((e for e in entries if e['return_id']==r['return_id'] and e.get('reversed')),None)
    if old:
        proof=OutboxEvent.objects.get(pk=returns.key(returns.VOIDED,company.pk,invoice_id,r['return_id']));p=returns.read(proof,returns.VOIDED,company)
        if p['review_id']!=review_id:raise AccountingError('Correction already applied by another review; recover current state.')
        return returns.response(company,invoice_id,body,entries,used,head,journal_id=p['journal_id'],replayed=True,ledger_written=True)
    target=active_target(entries,r['return_id'])
    if r['history_digest']!=head or r['revision']!=len(entries) or r['void_index']!=sum(bool(e.get('reversed')) for e in entries)+1 or r['target_journal_id']!=target['journal_id'] or timezone.now()>=timezone.datetime.fromisoformat(r['expires_at']):raise AccountingError('Stale/expired correction review; recover state.')
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=r['entry_date'],period_end__gte=r['entry_date'])[:2])
    if len(periods)!=1 or str(periods[0].pk)!=r['period_id']:raise AccountingError('Correction period changed.')
    lines=[]
    for line in r['lines']:
        account=Account.plain_objects.filter(pk=line['account_id'],tenant=company,chart_of_accounts__tenant=company,is_active=True).first();roles={'BASIS':{'ASSET','EXPENSE'},'INPUT_TAX':{'ASSET'},'WITHHOLDING':{'LIABILITY'},'SETTLEMENT':{'LIABILITY'}}
        if account is None or account.type not in roles[line['kind']]:raise AccountingError('Correction account unavailable or changed.')
        lines.append({'account':account,'debit':line['debit'],'credit':line['credit']})
    event=returns.event_key(source['journal_id'],'void:'+r['return_id'])
    if AccountingEventReceipt.objects.filter(tenant=company,event_id=event).exists():raise AccountingError('Missing correction proof; no reconstruction.')
    journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=date.fromisoformat(r['entry_date']),description='Reviewed native return correction',lines_data=lines,actor=user,idempotency_key=event,period_id=r['period_id'])
    returns.store(returns.VOIDED,company,{'company_id':str(company.pk),'provider_id':str(provider.pk),'invoice_id':invoice_id,'return_id':r['return_id'],'revision':r['revision'],'void_index':r['void_index'],'original_journal_id':source['journal_id'],'target_journal_id':target['journal_id'],'review_id':review_id,'review_digest':fingerprint(r),'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    entries,used,head=returns.history(company,invoice_id,body,source)
    return returns.response(company,invoice_id,body,entries,used,head,journal_id=str(journal.pk),replayed=False,ledger_written=True)
