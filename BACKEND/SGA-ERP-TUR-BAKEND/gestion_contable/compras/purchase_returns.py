"""Reviewed proportional returns of single-concept unpaid COP native purchases.
Append-only contra postings, not payments, DIAN credit notes or invoice edits.
"""
from uuid import UUID,uuid5
from datetime import date,timedelta
from decimal import Decimal,localcontext,ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting import commercial_tax_posting as ledger
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import _money,_format_money
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry,Account,FiscalPeriod,AccountingEventReceipt
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from . import native_purchase as native
NS=UUID('28d532cf-014d-43ad-b93f-91d8a7b4fdcc')
REVIEW='accounting.native-return.reviewed.v1'
POSTED='accounting.native-return.posted.v1'
DOCUMENT='accounting.native-return.document-claimed.v1'
VOID_REVIEW='accounting.native-return.void-reviewed.v1'
VOIDED='accounting.native-return.voided.v1'

def key(kind,company,invoice,identifier):return uuid5(NS,kind+':'+str(company)+':'+str(invoice)+':'+str(identifier))
def event_key(original,return_id):return 'purchase-return:'+str(original)+':'+return_id

def read(row,kind,company):
    if row is None or row.event_type!=kind or row.domain!='accounting' or row.version!=1 or set(row.payload)!={'body','digest'}:raise AccountingError('Return evidence missing.')
    body=row.payload['body']
    if not isinstance(body,dict):raise AccountingError('Return body missing.')
    if body.get('company_id')!=str(company.pk) or row.aggregate_root!=str(company.pk)+':'+str(body['invoice_id']) or fingerprint(body)!=row.payload['digest']:raise AccountingError('Return evidence changed.')
    identity=body['request_id'] if kind==VOID_REVIEW else body['return_id'] if kind in {POSTED,VOIDED} else body['return_id']+':'+str(body['revision'])
    if row.pk!=key(kind,company.pk,body['invoice_id'],identity):raise AccountingError('Return identity changed.')
    return body

def store(kind,company,body):
    identity=body['request_id'] if kind==VOID_REVIEW else body['return_id'] if kind in {POSTED,VOIDED} else body['return_id']+':'+str(body['revision'])
    return OutboxEvent.objects.create(id=key(kind,company.pk,body['invoice_id'],identity),event_type=kind,domain='accounting',aggregate_root=str(company.pk)+':'+str(body['invoice_id']),payload={'body':body,'digest':fingerprint(body)},version=1)

def original(company,document_id):
    review,body,proof,state=ledger.original_state(company,document_id)
    identity=body.get('source_binding',{}).get('identity',{})
    if body['fact']['direction']!='PURCHASE' or identity.get('kind')!='ERP_PURCHASE' or len(body['fact']['items'])!=1:raise AccountingError('Posted native single-concept purchase required.')
    marker=OutboxEvent.objects.filter(pk=uuid5(native.NS,'posted:'+str(company.pk)+':'+str(identity['invoice_id']))).first()
    expected={'company_id':str(company.pk),'provider_id':identity['provider_id'],'invoice_id':identity['invoice_id'],'review_id':str(review.pk),'binding_digest':fingerprint(body['source_binding']),'journal_id':state['journal_id']}
    if marker is None or marker.event_type!=native.POSTED or marker.domain!='accounting' or marker.version!=1 or marker.aggregate_root!=str(company.pk) or marker.payload!=expected:raise AccountingError('Native purchase origin requires reconciliation.')
    if len({r['kind'] for r in body['preview']['lines']})!=len(body['preview']['lines']) or not set(r['kind'] for r in body['preview']['lines'])<={'BASIS','INPUT_TAX','WITHHOLDING','SETTLEMENT'}:raise AccountingError('Distinct single-concept components required.')
    return body,state

def money_totals(original_totals,net):
    with localcontext() as ctx:
        ctx.prec=38
        def proportional(k):return int((Decimal(_money(original_totals[k]))*Decimal(net)/Decimal(_money(original_totals['net']))).quantize(Decimal(1),rounding=ROUND_HALF_UP))
        tax=proportional('tax');ret=proportional('withholding')
    return {'net':net,'tax':tax,'withholding':ret,'gross':net+tax,'settlement':net+tax-ret}

def contra_lines(original_body,totals):
    if any(v<0 for v in totals.values()):raise AccountingError('Negative rounded component unsupported; reviewed reconciliation required.')
    names={'BASIS':'net','INPUT_TAX':'tax','WITHHOLDING':'withholding','SETTLEMENT':'settlement'};result=[]
    for line in original_body['preview']['lines']:
        amount=totals[names[line['kind']]]
        if amount:result.append({'account_id':line['account_id'],'kind':line['kind'],'debit':_format_money(amount if line['credit']!='0.00' else 0),'credit':_format_money(amount if line['debit']!='0.00' else 0)})
    if sum(_money(r['debit']) for r in result)!=sum(_money(r['credit']) for r in result):raise AccountingError('Return contra entries must balance exactly.')
    return result

def validate_post(company,proof,origin_body,origin_state):
    body=read(proof,POSTED,company);review=OutboxEvent.objects.filter(pk=body['review_id']).first();proposal=read(review,REVIEW,company)
    if body['review_digest']!=fingerprint(proposal) or body['return_id']!=proposal['return_id'] or body['invoice_id']!=proposal['invoice_id'] or body['original_journal_id']!=origin_state['journal_id'] or proposal['original_hash']!=origin_state_hash(origin_state,company) or proposal['document_id']!=origin_body['document_id']:raise AccountingError('Return source changed.')
    journal=JournalEntry.plain_objects.filter(pk=body['journal_id'],tenant=company,is_posted=True,is_reversal=False).first()
    if journal is None or journal.financial_event_id!=event_key(body['original_journal_id'],body['return_id']) or journal.system_hash!=body['journal_hash'] or journal.compute_hash()!=body['journal_hash'] or journal.date.isoformat()!=proposal['entry_date'] or str(journal.period_id)!=proposal['period_id'] or str(journal.created_by_id)!=proposal['reviewed_by']:raise AccountingError('Return journal integrity changed.')
    if JournalEntry.plain_objects.filter(tenant=company,reversed_entry_id=journal.pk,is_posted=True).exists():raise AccountingError('Unreviewed return reversal requires reconciliation.')
    actual=sorted((str(r.account_id),format(r.debit_amount,'.2f'),format(r.credit_amount,'.2f')) for r in LedgerEntry.plain_objects.filter(tenant=company,journal_entry=journal))
    if actual!=sorted((r['account_id'],r['debit'],r['credit']) for r in proposal['lines']):raise AccountingError('Return lines changed.')
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=journal.financial_event_id,journal=journal).first()
    contract={'schema':'manual-journal-v2','tenant_id':str(company.pk),'actor_id':journal.created_by_id,'date':proposal['entry_date'],'description':'Reviewed native purchase return','period_id':proposal['period_id'],'lines':[{'account':r['account_id'],'debit':r['debit'],'credit':r['credit']} for r in proposal['lines']]}
    if receipt is None or receipt.payload_hash!=fingerprint(contract):raise AccountingError('Return receipt changed.')
    claim=OutboxEvent.objects.filter(pk=uuid5(NS,'document:'+str(company.pk)+':'+proposal['document_digest'])).first()
    expected={'company_id':str(company.pk),'return_proof_id':str(proof.pk),'document_digest':proposal['document_digest']}
    if claim is None or claim.event_type!=DOCUMENT or claim.domain!='accounting' or claim.version!=1 or claim.aggregate_root!=str(company.pk) or claim.payload!=expected:raise AccountingError('Return document reservation changed.')
    return proposal

def origin_state_hash(state,company):return JournalEntry.plain_objects.get(pk=state['journal_id'],tenant=company).system_hash

def history(company,invoice_id,body,state):
    if OutboxEvent.objects.filter(event_type='accounting.native-purchase.returned.v1',aggregate_root=str(company.pk),payload__body__invoice_id=invoice_id).exists():raise AccountingError('This invoice uses the published proportional return protocol; reconcile it there before changing protocol.')
    from .purchase_return_voids import validate_proof
    query=OutboxEvent.objects.filter(payload__body__company_id=str(company.pk),payload__body__invoice_id=invoice_id)
    proofs=list(query.filter(event_type=POSTED).order_by('payload__body__revision')[:31]);voids=list(query.filter(event_type=VOIDED).order_by('payload__body__void_index')[:31])
    if len(proofs)>30 or len(voids)>30:raise AccountingError('At most30 returns/corrections per invoice; reviewed archival required.')
    journals=set(str(v) for v in JournalEntry.plain_objects.filter(tenant=company,is_posted=True,financial_event_id__startswith='purchase-return:'+state['journal_id']+':').values_list('pk',flat=True))
    receipt_journals=set(str(v) for v in AccountingEventReceipt.objects.filter(tenant=company,event_id__startswith='purchase-return:'+state['journal_id']+':').values_list('journal_id',flat=True))
    if receipt_journals!=journals:raise AccountingError('Return receipt/journal history inconsistent.')
    if journals!=set(p.payload['body']['journal_id'] for p in proofs+voids):raise AccountingError('Return/correction journal or proof missing; capacity cannot be inferred.')
    grouped={}
    for proof in voids:
        v=read(proof,VOIDED,company)
        if type(v['revision']) is not int or not 1<=v['revision']<=len(proofs):raise AccountingError('Correction position changed.')
        grouped.setdefault(v['revision'],[]).append(proof)
    used={k:0 for k in body['preview']['totals']};entries=[];previous=fingerprint([]);void_index=0;origins={}
    for revision,proof in enumerate(proofs,1):
        p=read(proof,POSTED,company);r=validate_post(company,proof,body,state)
        if p['revision']!=revision or r['revision']!=revision or r['history_digest']!=previous:raise AccountingError('Return sequence changed.')
        after=money_totals(body['preview']['totals'],used['net']+_money(r['totals']['net']))
        if after['net']>_money(body['preview']['totals']['net']) or any(_money(r['totals'][k])!=after[k]-used[k] for k in used) or r['lines']!=contra_lines(body,{k:after[k]-used[k] for k in used}):raise AccountingError('Return allocation exceeds original capacity or changes original proportions.')
        used=after;entries.append({'return_id':p['return_id'],'journal_id':p['journal_id'],'review_id':p['review_id'],'revision':revision,'totals':r['totals'],'proof_digest':proof.payload['digest']});origins[p['return_id']]=(proof,r);previous=fingerprint(entries)
        for correction in grouped.get(revision,[]):
            v=read(correction,VOIDED,company);active=[e for e in entries if not e.get('reversed')]
            if not active or active[-1]['return_id']!=v['return_id'] or type(v['void_index']) is not int or v['void_index']!=void_index+1:raise AccountingError('Corrections must reverse the last active return in order.')
            target=active[-1];target_proof,target_review=origins[target['return_id']];proposal=validate_proof(company,correction,body,state,target_proof,target_review)
            if proposal['revision']!=revision or proposal['history_digest']!=previous:raise AccountingError('Correction history changed.')
            used={k:used[k]-_money(target['totals'][k]) for k in used}
            if any(v<0 for v in used.values()) or used!=money_totals(body['preview']['totals'],used['net']):raise AccountingError('Correction cannot release extra cents or capacity.')
            target.update(reversed=True,reversal_journal_id=v['journal_id'],reversal_digest=correction.payload['digest']);previous=fingerprint(entries);void_index+=1
    return entries,used,previous

def context(actor,provider_id,invoice_id,require_unchanged=False,allow_reversed=False):
    user,provider,company=native.context(actor,provider_id);row=native.invoice(provider,invoice_id);state=native.purchase_state(actor=user,provider_id=provider.pk,invoice_id=invoice_id)
    if state['posted'] is None:raise AccountingError('Posted native invoice required.')
    body,source=original(company,native.document(company,row))
    if source['reversed'] and not allow_reversed:raise AccountingError('Original is already fully reversed.')
    if require_unchanged and (not state['source_matches_review'] or row.estado not in {'POR_PAGAR','VENCIDA'}):raise AccountingError('Unchanged unpaid source required; no cash refund inferred.')
    entries,used,head=history(company,invoice_id,body,source)
    return user,provider,company,row,body,source,entries,used,head

def response(company,invoice_id,body,entries,used,head,**extra):
    return {'schema':'sgacd-native-purchase-return-v1','native_source_verified':True,'company_id':str(company.pk),'invoice_id':invoice_id,'document_id':body['document_id'],'returns':entries,'revision':len(entries),'history_digest':head,'returned':{k:_format_money(v) for k,v in used.items()},'remaining':{k:_format_money(_money(body['preview']['totals'][k])-v) for k,v in used.items()},'currency':'COP','money_transferred':False,'fiscal_document_created':False,'regulatory_verified':False,'confirmations_restored':False,**extra}

@transaction.atomic
def state(*,actor,provider_id,invoice_id):
    _,_,company,_,body,source,entries,used,head=context(actor,provider_id,invoice_id,allow_reversed=True)
    if source['reversed'] and (any(used.values()) or any(not row.get('reversed') for row in entries)):raise AccountingError('Full original reversal conflicts with active returns.')
    result=response(company,invoice_id,body,entries,used,head,read_only=True,ledger_written=False,original_reversed=source['reversed'])
    if source['reversed']:result['remaining']={k:'0.00' for k in result['remaining']}
    return result

@transaction.atomic
def review(*,actor,provider_id,invoice_id,return_id,net_amount,entry_date,document_digest,evidence_digest,expected_revision,confirmed):
    user,provider,company,row,body,source,entries,used,head=context(actor,provider_id,invoice_id,True);ledger.identifier(return_id);ledger.digest(document_digest);ledger.digest(evidence_digest)
    amount=_money(net_amount);day=date.fromisoformat(entry_date)
    if confirmed is not True or type(expected_revision) is not int or expected_revision!=len(entries) or amount<=0 or amount+used['net']>_money(body['preview']['totals']['net']) or day.isoformat()!=entry_date or entry_date<body['fact']['entry_date'] or day>timezone.localdate():raise AccountingError('Exact available positive net amount, date, revision and first confirmation required.')
    if len(entries)>=30:raise AccountingError('Return history full.')
    if any(r['return_id']==return_id for r in entries):raise AccountingError('Return already posted; recover it.')
    if OutboxEvent.objects.filter(pk=uuid5(NS,'document:'+str(company.pk)+':'+document_digest)).exists():raise AccountingError('Return document already consumed.')
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=day,period_end__gte=day)[:2])
    if len(periods)!=1:raise AccountingError('Unique open return period required.')
    totals=money_totals(body['preview']['totals'],used['net']+amount);delta={k:totals[k]-used[k] for k in used};lines=contra_lines(body,delta)
    content={'company_id':str(company.pk),'provider_id':str(provider.pk),'invoice_id':invoice_id,'document_id':body['document_id'],'return_id':return_id,'revision':len(entries)+1,'history_digest':head,'original_journal_id':source['journal_id'],'original_hash':origin_state_hash(source,company),'reviewed_by':str(user.pk),'entry_date':entry_date,'period_id':str(periods[0].pk),'document_digest':document_digest,'evidence_digest':evidence_digest,'totals':{k:_format_money(v) for k,v in delta.items()},'lines':lines}
    old=OutboxEvent.objects.filter(pk=key(REVIEW,company.pk,invoice_id,return_id+':'+str(len(entries)+1))).first()
    if old:
        saved=read(old,REVIEW,company)
        if {k:v for k,v in saved.items() if k!='expires_at'}!=content:raise AccountingError('Review identity already bound to different return.')
        content=saved
    else:content['expires_at']=(timezone.now()+timedelta(minutes=15)).isoformat();old=store(REVIEW,company,content)
    return {'company_id':str(company.pk),'invoice_id':invoice_id,'return_id':return_id,'review_id':str(old.pk),'preview':content,'ledger_written':False,'money_transferred':False,'regulatory_verified':False,'fiscal_document_created':False}

@transaction.atomic
def post(*,actor,provider_id,invoice_id,review_id,confirmed):
    user,provider,company,row,body,source,entries,used,head=context(actor,provider_id,invoice_id);ledger.identifier(review_id);proposal_row=OutboxEvent.objects.filter(pk=review_id).first();p=read(proposal_row,REVIEW,company)
    if confirmed is not True or p['reviewed_by']!=str(user.pk) or p['invoice_id']!=invoice_id or p['provider_id']!=str(provider.pk):raise AccountingError('Second confirmation by same owner required.')
    old=next((r for r in entries if r['return_id']==p['return_id']),None)
    if old:
        if old['review_id']!=review_id:raise AccountingError('Return identity already used.')
        return response(company,invoice_id,body,entries,used,head,journal_id=old['journal_id'],replayed=True,ledger_written=True)
    context(actor,provider_id,invoice_id,True)
    if p['revision']!=len(entries)+1 or p['history_digest']!=head or p['original_hash']!=origin_state_hash(source,company) or timezone.now()>=timezone.datetime.fromisoformat(p['expires_at']):raise AccountingError('Stale or expired return review; recover current capacity.')
    if AccountingEventReceipt.objects.filter(tenant=company,event_id=event_key(source['journal_id'],p['return_id'])).exists():raise AccountingError('Missing return proof; no reconstruction.')
    claim_id=uuid5(NS,'document:'+str(company.pk)+':'+p['document_digest'])
    if OutboxEvent.objects.filter(pk=claim_id).exists():raise AccountingError('Return document already consumed.')
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=p['entry_date'],period_end__gte=p['entry_date'])[:2])
    if len(periods)!=1 or str(periods[0].pk)!=p['period_id']:raise AccountingError('Return period changed.')
    lines=[]
    for item in p['lines']:
        account=Account.plain_objects.filter(pk=item['account_id'],tenant=company,chart_of_accounts__tenant=company,is_active=True).first()
        expected_types={'BASIS':{'ASSET','EXPENSE'},'INPUT_TAX':{'ASSET'},'WITHHOLDING':{'LIABILITY'},'SETTLEMENT':{'LIABILITY'}}
        if account is None or account.type not in expected_types[item['kind']]:raise AccountingError('Return account no longer available or role changed.')
        lines.append({'account':account,'debit':item['debit'],'credit':item['credit']})
    journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=date.fromisoformat(p['entry_date']),description='Reviewed native purchase return',lines_data=lines,actor=user,idempotency_key=event_key(source['journal_id'],p['return_id']),period_id=p['period_id'])
    proof=store(POSTED,company,{'company_id':str(company.pk),'provider_id':str(provider.pk),'invoice_id':invoice_id,'return_id':p['return_id'],'revision':p['revision'],'original_journal_id':source['journal_id'],'review_id':review_id,'review_digest':fingerprint(p),'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    OutboxEvent.objects.create(id=claim_id,event_type=DOCUMENT,domain='accounting',aggregate_root=str(company.pk),payload={'company_id':str(company.pk),'return_proof_id':str(proof.pk),'document_digest':p['document_digest']},version=1)
    entries,used,head=history(company,invoice_id,body,source)
    return response(company,invoice_id,body,entries,used,head,journal_id=str(journal.pk),replayed=False,ledger_written=True)

def register_body(company,journal):
    proof=OutboxEvent.objects.filter(event_type__in=[POSTED,VOIDED],payload__body__company_id=str(company.pk),payload__body__journal_id=str(journal.pk)).first()
    if proof is None:raise AccountingError('Return/correction origin missing.')
    p=read(proof,proof.event_type,company);review=read(OutboxEvent.objects.filter(pk=p['review_id']).first(),REVIEW if proof.event_type==POSTED else VOID_REVIEW,company);body,source=original(company,review['document_id']);history(company,p['invoice_id'],body,source)
    return {'document_id':body['document_id'],'preview':{'lines':review['lines']}}
