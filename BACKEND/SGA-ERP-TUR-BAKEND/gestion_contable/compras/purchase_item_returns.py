"""Reviewed returns by concept for multi-concept unpaid COP native purchases.
Cumulative proportions use the posted original, never current tax rates or cash.
"""
from datetime import date,timedelta
from uuid import UUID,uuid5
from django.db import transaction
from django.utils import timezone
from apps.core_erp.accounting import commercial_tax_posting as ledger
from apps.core_erp.accounting.integrity import fingerprint
from apps.core_erp.accounting.invoice_intent import _money,_format_money
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.models import Account,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt
from apps.core_erp.accounting.ledger_engine import LedgerEngine
from apps.core_erp.outbox_models import OutboxEvent
from . import native_purchase as native,purchase_returns as single
NS=UUID('9420e7b2-5d49-4b6c-927a-017cffb7cd6f')
REVIEW='accounting.native-item-return.reviewed.v1'
POSTED='accounting.native-item-return.posted.v1'
VOID_REVIEW='accounting.native-item-return.void-reviewed.v1'
VOIDED='accounting.native-item-return.voided.v1'
PREFIX='purchase-item-return:'
REASONS={'DATA_ENTRY_ERROR','DUPLICATE_RETURN','SOURCE_WITHDRAWN'}

def key(kind,company,invoice,identity):return uuid5(NS,kind+':'+str(company)+':'+str(invoice)+':'+identity)
def identity(kind,b):return b['request_id'] if kind==VOID_REVIEW else b['return_id']+':'+str(b['revision']) if kind==REVIEW else b['return_id']
def store(kind,company,body):return OutboxEvent.objects.create(id=key(kind,company.pk,body['invoice_id'],identity(kind,body)),event_type=kind,domain='accounting',aggregate_root=str(company.pk)+':'+str(body['invoice_id']),version=1,payload={'body':body,'digest':fingerprint(body)})
def read(row,kind,company):
    if row is None or row.event_type!=kind or row.domain!='accounting' or row.version!=1 or not isinstance(row.payload,dict) or set(row.payload)!={'body','digest'}:raise AccountingError('Concept return evidence missing.')
    b=row.payload['body']
    if not isinstance(b,dict) or b.get('company_id')!=str(company.pk) or row.payload['digest']!=fingerprint(b) or row.aggregate_root!=str(company.pk)+':'+str(b['invoice_id']) or row.pk!=key(kind,company.pk,b['invoice_id'],identity(kind,b)):raise AccountingError('Concept return evidence changed.')
    return b

def original(company,document):
    review,body,proof,state=ledger.original_state(company,document);binding=body.get('source_binding',{});source=binding.get('identity',{})
    if body['fact']['direction']!='PURCHASE' or source.get('kind')!='ERP_PURCHASE' or not 2<=len(body['fact']['items'])<=20:raise AccountingError('Posted multi-concept native purchase required; do not change single-concept protocol.')
    marker=OutboxEvent.objects.filter(pk=uuid5(native.NS,'posted:'+str(company.pk)+':'+str(source['invoice_id']))).first()
    expected={'company_id':str(company.pk),'provider_id':source['provider_id'],'invoice_id':source['invoice_id'],'review_id':str(review.pk),'binding_digest':fingerprint(binding),'journal_id':state['journal_id']}
    if marker is None or marker.event_type!=native.POSTED or marker.domain!='accounting' or marker.version!=1 or marker.aggregate_root!=str(company.pk) or marker.payload!=expected:raise AccountingError('Native multi-concept source proof changed.')
    return body,state

def originals(body):
    quotes={q['item_id']:q for q in body['preview']['quotes']};result={}
    for item in body['fact']['items']:
        components=[]
        for c in quotes[item['item_id']]['components']:
            amount=_money(c['amount']);kind=c['kind']
            if amount and kind not in {'INPUT_TAX','WITHHOLDING'}:raise AccountingError('Unsupported posted purchase component.')
            components.append({'code':c['code'],'kind':kind,'amount':amount,'account_id':item['tax_accounts'].get(c['code'])})
        result[item['item_id']]={'item':item,'net':_money(item['net']),'components':components}
    if len(result)!=len(body['fact']['items']):raise AccountingError('Duplicate original concept.')
    return result

def prorate(amount,net,original_net):return (amount*net*2+original_net)//(2*original_net)
def totals(net,components):
    tax=sum(c['amount'] for c in components if c['kind']!='WITHHOLDING');ret=sum(c['amount'] for c in components if c['kind']=='WITHHOLDING')
    if net+tax-ret<0:raise AccountingError('Rounded withholding exceeds this allocation; reviewed reconciliation required.')
    return {'net':net,'tax':tax,'withholding':ret,'gross':net+tax,'settlement':net+tax-ret}
def amounts(values):return {k:_format_money(v) for k,v in values.items()}

def plan(body,used,selection):
    known=originals(body)
    if not isinstance(selection,list) or not 1<=len(selection)<=20:raise AccountingError('One to20 explicit concept net allocations required.')
    seen=set();items=[];lines=[];total={k:0 for k in ('net','tax','withholding','gross','settlement')}
    def line(account,amount,debit,kind):
        if amount:lines.append({'account_id':account,'debit':_format_money(amount if debit else 0),'credit':_format_money(0 if debit else amount),'kind':kind})
    for entry in sorted(selection,key=lambda e:e.get('item_id','') if isinstance(e,dict) else ''):
        if not isinstance(entry,dict) or set(entry)!={'item_id','net'}:raise AccountingError('Explicit concept identity and net required.')
        item_id=ledger.identifier(entry['item_id']);net=_money(entry['net'])
        if item_id not in known or item_id in seen or net<=0:raise AccountingError('Unique actual positive concept required.')
        seen.add(item_id);origin=known[item_id];before=used[item_id];after=before+net
        if after>origin['net']:raise AccountingError('Return exceeds remaining concept net.')
        components=[];delta=[];cumulative=[]
        for c in origin['components']:
            prior=prorate(c['amount'],before,origin['net']);current=prorate(c['amount'],after,origin['net']);difference=current-prior
            components.append({'code':c['code'],'kind':c['kind'],'account_id':c['account_id'],'original_amount':_format_money(c['amount']),'previous_amount':_format_money(prior),'new_amount':_format_money(current),'delta_amount':_format_money(difference)})
            delta.append({'kind':c['kind'],'amount':difference});cumulative.append({'kind':c['kind'],'amount':current})
        values=totals(net,delta);original_totals=totals(origin['net'],origin['components']);cumulative_totals=totals(after,cumulative)
        if any(cumulative_totals[k]>original_totals[k] for k in original_totals):raise AccountingError('Rounded allocation exceeds original settlement capacity; review a combined amount.')
        item=origin['item'];line(item['basis_account_id'],net,False,'BASIS')
        for c in components:line(c['account_id'],_money(c['delta_amount']),c['kind']=='WITHHOLDING',c['kind'])
        items.append({'item_id':item_id,'basis_account_id':item['basis_account_id'],'original_net':_format_money(origin['net']),'previous_net':_format_money(before),'net':_format_money(net),'new_net':_format_money(after),'components':components,'totals':amounts(values)})
        for k in total:total[k]+=values[k]
    line(body['fact']['settlement_account_id'],total['settlement'],True,'SETTLEMENT')
    if len(lines)<2 or sum(_money(r['debit']) for r in lines)!=sum(_money(r['credit']) for r in lines):raise AccountingError('Concept contra journal does not balance.')
    return {'selection':[{'item_id':i['item_id'],'net':i['net']} for i in items],'allocations':items,'totals':amounts(total),'lines':lines}

def claim_id(company,digest):return uuid5(single.NS,'document:'+str(company.pk)+':'+digest)
def event_id(original_id,return_id,void=False):return PREFIX+str(original_id)+':'+('void:' if void else '')+return_id

def verify_post(company,event,body,state):
    p=read(event,event.event_type,company);review=OutboxEvent.objects.filter(pk=p['review_id']).first();r=read(review,VOID_REVIEW if event.event_type==VOIDED else REVIEW,company)
    if p['review_digest']!=fingerprint(r) or any(p[k]!=r[k] for k in ('invoice_id','return_id','revision')) or p['original_journal_id']!=state['journal_id'] or r['original_journal_id']!=state['journal_id'] or r['original_hash']!=JournalEntry.plain_objects.get(pk=state['journal_id'],tenant=company).system_hash or r['document_id']!=body['document_id']:raise AccountingError('Concept return origin/review changed.')
    journal=JournalEntry.plain_objects.filter(pk=p['journal_id'],tenant=company,is_posted=True,is_reversal=False).first();void=event.event_type==VOIDED
    if journal is None or journal.financial_event_id!=event_id(state['journal_id'],r['return_id'],void) or journal.system_hash!=p['journal_hash'] or journal.compute_hash()!=p['journal_hash'] or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=1 or journal.date.isoformat()!=r['entry_date'] or str(journal.period_id)!=r['period_id'] or str(journal.created_by_id)!=r['reviewed_by'] or JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id=journal.pk).exists():raise AccountingError('Concept return journal integrity changed.')
    records=list(LedgerEntry.plain_objects.filter(journal_entry=journal,tenant=company))
    if sorted((str(l.account_id),format(l.debit_amount,'.2f'),format(l.credit_amount,'.2f')) for l in records)!=sorted((l['account_id'],l['debit'],l['credit']) for l in r['lines']) or any(l.currency!='COP' or l.amount_transaction!=l.debit_amount+l.credit_amount or l.amount_base!=l.debit_amount+l.credit_amount for l in records):raise AccountingError('Concept return journal lines/valuation changed.')
    description='Reviewed concept return correction' if void else 'Reviewed purchase return by concept'
    contract={'schema':'manual-journal-v2','tenant_id':str(company.pk),'actor_id':journal.created_by_id,'date':r['entry_date'],'description':description,'period_id':r['period_id'],'lines':[{'account':l['account_id'],'debit':l['debit'],'credit':l['credit']} for l in r['lines']]}
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=journal.financial_event_id,journal=journal).first()
    if receipt is None or receipt.payload_hash!=fingerprint(contract):raise AccountingError('Concept return receipt changed.')
    if not void:
        claim=OutboxEvent.objects.filter(pk=claim_id(company,r['document_digest'])).first()
        if claim is None or claim.event_type!=single.DOCUMENT or claim.domain!='accounting' or claim.aggregate_root!=str(company.pk) or claim.version!=1 or claim.payload!={'company_id':str(company.pk),'invoice_id':r['invoice_id'],'return_proof_id':str(event.pk),'document_digest':r['document_digest']}:raise AccountingError('Concept return support reservation changed.')
    return p,r

def history(company,invoice_id,body,state):
    q=OutboxEvent.objects.filter(payload__body__company_id=str(company.pk),payload__body__invoice_id=invoice_id)
    posted=list(q.filter(event_type=POSTED).order_by('payload__body__revision')[:31]);voided=list(q.filter(event_type=VOIDED).order_by('payload__body__void_index')[:31])
    if len(posted)>30 or len(voided)>30:raise AccountingError('Reviewed extended concept-return history required.')
    if q.filter(event_type__in=[single.POSTED,single.VOIDED,'accounting.native-purchase.returned.v1']).exists():raise AccountingError('Do not mix return protocols for an invoice.')
    prefix=PREFIX+state['journal_id']+':'
    journals={str(v) for v in JournalEntry.plain_objects.filter(tenant=company,is_posted=True,financial_event_id__startswith=prefix).values_list('pk',flat=True)}
    receipts={str(v) for v in AccountingEventReceipt.objects.filter(tenant=company,event_id__startswith=prefix).values_list('journal_id',flat=True)}
    if journals!=receipts or journals!={p.payload['body']['journal_id'] for p in posted+voided}:raise AccountingError('Concept return journal/receipt/proof history incomplete.')
    used={k:0 for k in originals(body)};expected_claims=set();entries=[];head=fingerprint([]);void_index=0;by_revision={};sources={}
    for event in voided:
        p=read(event,VOIDED,company)
        if type(p.get('revision')) is not int or not 1<=p['revision']<=len(posted):raise AccountingError('Concept correction position changed.')
        by_revision.setdefault(p['revision'],[]).append(event)
    for revision,event in enumerate(posted,1):
        p,r=verify_post(company,event,body,state);expected_claims.add(claim_id(company,r['document_digest']))
        expected=plan(body,used,r['selection'])
        if p['revision']!=revision or r['history_digest']!=head or any(r[k]!=expected[k] for k in expected):raise AccountingError('Concept return capacity/proportion changed.')
        for allocation in r['selection']:used[allocation['item_id']]+=_money(allocation['net'])
        entry={'return_id':p['return_id'],'review_id':p['review_id'],'journal_id':p['journal_id'],'revision':revision,'selection':r['selection'],'totals':r['totals'],'proof_digest':event.payload['digest']};entries.append(entry);sources[p['return_id']]=(event,r);head=fingerprint(entries)
        for correction in by_revision.get(revision,[]):
            v,proposal=verify_post(company,correction,body,state);active=[e for e in entries if not e.get('reversed')]
            if not active or active[-1]['return_id']!=v['return_id'] or v['void_index']!=void_index+1 or proposal['void_index']!=v['void_index'] or proposal['history_digest']!=head:raise AccountingError('Correct latest active concept return first; history changed.')
            target=active[-1];target_event,target_review=sources[v['return_id']]
            opposite=[{**l,'debit':l['credit'],'credit':l['debit']} for l in target_review['lines']]
            if proposal['target_proof_digest']!=target_event.payload['digest'] or proposal['target_journal_id']!=target['journal_id'] or proposal['lines']!=opposite or proposal['selection']!=target_review['selection'] or proposal['totals']!=target_review['totals']:raise AccountingError('Concept correction no longer matches original allocation.')
            for a in proposal['selection']:used[a['item_id']]-=_money(a['net'])
            if any(v<0 for v in used.values()):raise AccountingError('Concept correction releases excess capacity.')
            target.update(reversed=True,reversal_journal_id=v['journal_id'],reversal_digest=correction.payload['digest']);void_index+=1;head=fingerprint(entries)
    actual_claims=set(OutboxEvent.objects.filter(event_type=single.DOCUMENT,payload__company_id=str(company.pk),payload__invoice_id=invoice_id).values_list('pk',flat=True))
    if actual_claims!=expected_claims:raise AccountingError('Orphan or missing concept return support requires reconciliation.')
    return entries,used,head

def context(actor,provider_id,invoice_id,writable=False):
    user,provider,company=native.context(actor,provider_id);row=native.invoice(provider,invoice_id);current=native.purchase_state(actor=user,provider_id=provider.pk,invoice_id=invoice_id)
    if current['posted'] is None:raise AccountingError('Posted native purchase required.')
    body,state=original(company,native.document(company,row));entries,used,head=history(company,invoice_id,body,state)
    if state['reversed'] and (any(used.values()) or any(not e.get('reversed') for e in entries)):raise AccountingError('Original reversed despite active concept returns; reconcile history.')
    if writable and (state['reversed'] or not current['source_matches_review'] or row.estado not in {'POR_PAGAR','VENCIDA'}):raise AccountingError('Unchanged unpaid unreversed source required; no cash refund inferred.')
    return user,provider,company,body,state,entries,used,head

def response(company,invoice_id,body,state,entries,used,head,**extra):
    items=[]
    for item_id,origin in originals(body).items():
        returned_components=[{**c,'amount':prorate(c['amount'],used[item_id],origin['net'])} for c in origin['components']];original_totals=totals(origin['net'],origin['components']);returned=totals(used[item_id],returned_components)
        items.append({'item_id':item_id,'basis_account_id':origin['item']['basis_account_id'],'tax_category':origin['item']['tax_category'],'policy_code':origin['item']['policy_code'],'policy_revision':origin['item']['policy_revision'],'available_net':'0.00' if state['reversed'] else _format_money(origin['net']-used[item_id]),'original':amounts(original_totals),'returned':amounts(returned),'remaining':amounts({k:original_totals[k]-returned[k] for k in original_totals})})
    return {'schema':'sgacd-purchase-item-returns-v1','company_id':str(company.pk),'invoice_id':invoice_id,'document_id':body['document_id'],'original_journal_id':state['journal_id'],'original_reversed':state['reversed'],'currency':'COP','items':items,'returns':entries,'revision':len(entries),'history_digest':head,'money_transferred':False,'regulatory_verified':False,'fiscal_document_created':False,'confirmations_restored':False,**extra}

@transaction.atomic
def state(*,actor,provider_id,invoice_id):
    _,_,company,body,source,entries,used,head=context(actor,provider_id,invoice_id)
    return response(company,invoice_id,body,source,entries,used,head,read_only=True,ledger_written=False)

def period(company,day):
    parsed=date.fromisoformat(day)
    if parsed.isoformat()!=day or parsed>timezone.localdate():raise AccountingError('Canonical nonfuture return date required.')
    rows=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=parsed,period_end__gte=parsed)[:2])
    if len(rows)!=1:raise AccountingError('Unique open return period required.')
    return str(rows[0].pk)

def save_review(kind,company,content):
    old=OutboxEvent.objects.filter(pk=key(kind,company.pk,content['invoice_id'],identity(kind,content))).first()
    if old:
        saved=read(old,kind,company)
        if {k:v for k,v in saved.items() if k!='expires_at'}!=content:raise AccountingError('Return review identity already bound to other inputs.')
        return old,saved
    content['expires_at']=(timezone.now()+timedelta(minutes=15)).isoformat();return store(kind,company,content),content

def review_response(company,row,p):return {'company_id':str(company.pk),'invoice_id':p['invoice_id'],'return_id':p['return_id'],'review_id':str(row.pk),'preview':p,'ledger_written':False,'money_transferred':False,'regulatory_verified':False,'fiscal_document_created':False}

@transaction.atomic
def review(*,actor,provider_id,invoice_id,return_id,selection,entry_date,document_digest,evidence_digest,expected_revision,confirmed):
    user,provider,company,body,source,entries,used,head=context(actor,provider_id,invoice_id,True);ledger.identifier(return_id);ledger.digest(document_digest);ledger.digest(evidence_digest)
    if confirmed is not True or type(expected_revision) is not int or expected_revision!=len(entries) or len(entries)>=30 or entry_date<body['fact']['entry_date'] or any(e['return_id']==return_id for e in entries):raise AccountingError('First confirmation, current revision, source date and unused return identity required.')
    if OutboxEvent.objects.filter(pk=claim_id(company,document_digest)).exists():raise AccountingError('Support already consumed by a return; correction does not release it.')
    content={'company_id':str(company.pk),'provider_id':str(provider.pk),'invoice_id':invoice_id,'document_id':body['document_id'],'return_id':return_id,'revision':len(entries)+1,'history_digest':head,'original_journal_id':source['journal_id'],'original_hash':JournalEntry.plain_objects.get(pk=source['journal_id'],tenant=company).system_hash,'reviewed_by':str(user.pk),'entry_date':entry_date,'period_id':period(company,entry_date),'document_digest':document_digest,'evidence_digest':evidence_digest,**plan(body,used,selection)}
    row,p=save_review(REVIEW,company,content);return review_response(company,row,p)

def write_journal(company,user,p,void=False):
    if period(company,p['entry_date'])!=p['period_id']:raise AccountingError('Return period changed.')
    roles={'BASIS':{'ASSET','EXPENSE'},'INPUT_TAX':{'ASSET'},'WITHHOLDING':{'LIABILITY'},'SETTLEMENT':{'LIABILITY'}};lines=[]
    for l in p['lines']:
        account=Account.plain_objects.filter(pk=l['account_id'],tenant=company,chart_of_accounts__tenant=company,is_active=True,type__in=roles[l['kind']]).first()
        if account is None:raise AccountingError('Return account inactive, foreign or role changed.')
        lines.append({'account':account,'debit':l['debit'],'credit':l['credit']})
    event=event_id(p['original_journal_id'],p['return_id'],void)
    if AccountingEventReceipt.objects.filter(tenant=company,event_id=event).exists() or JournalEntry.plain_objects.filter(tenant=company,financial_event_id=event).exists():raise AccountingError('Financial origin exists without proof; no reconstruction.')
    return LedgerEngine.post_lines(tenant_id=company.pk,entry_date=date.fromisoformat(p['entry_date']),description='Reviewed concept return correction' if void else 'Reviewed purchase return by concept',lines_data=lines,actor=user,idempotency_key=event,period_id=p['period_id'])

@transaction.atomic
def post(*,actor,provider_id,invoice_id,review_id,confirmed):
    user,provider,company,body,source,entries,used,head=context(actor,provider_id,invoice_id);row=OutboxEvent.objects.filter(pk=ledger.identifier(review_id)).first();p=read(row,REVIEW,company)
    if confirmed is not True or p['reviewed_by']!=str(user.pk) or p['provider_id']!=str(provider.pk) or p['invoice_id']!=invoice_id:raise AccountingError('Second confirmation by same owner for this invoice required.')
    old=next((e for e in entries if e['return_id']==p['return_id']),None)
    if old:
        if old['review_id']!=review_id:raise AccountingError('Return already posted under another review.')
        return response(company,invoice_id,body,source,entries,used,head,journal_id=old['journal_id'],replayed=True,ledger_written=True)
    context(actor,provider_id,invoice_id,True)
    if p['history_digest']!=head or p['revision']!=len(entries)+1 or timezone.now()>=timezone.datetime.fromisoformat(p['expires_at']) or any(p[k]!=v for k,v in plan(body,used,p['selection']).items()):raise AccountingError('Return source/capacity/expiry changed; recover and review again.')
    if OutboxEvent.objects.filter(pk=claim_id(company,p['document_digest'])).exists():raise AccountingError('Return support already consumed.')
    journal=write_journal(company,user,p)
    proof=store(POSTED,company,{'company_id':str(company.pk),'invoice_id':invoice_id,'return_id':p['return_id'],'revision':p['revision'],'original_journal_id':source['journal_id'],'review_id':review_id,'review_digest':fingerprint(p),'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    OutboxEvent.objects.create(id=claim_id(company,p['document_digest']),event_type=single.DOCUMENT,domain='accounting',aggregate_root=str(company.pk),version=1,payload={'company_id':str(company.pk),'invoice_id':invoice_id,'return_proof_id':str(proof.pk),'document_digest':p['document_digest']})
    entries,used,head=history(company,invoice_id,body,source);return response(company,invoice_id,body,source,entries,used,head,journal_id=str(journal.pk),replayed=False,ledger_written=True)

@transaction.atomic
def review_void(*,actor,provider_id,invoice_id,return_id,request_id,entry_date,reason_code,evidence_digest,expected_revision,confirmed):
    user,provider,company,body,source,entries,used,head=context(actor,provider_id,invoice_id);ledger.identifier(request_id);ledger.digest(evidence_digest);active=[e for e in entries if not e.get('reversed')]
    if confirmed is not True or type(expected_revision) is not int or expected_revision!=len(entries) or reason_code not in REASONS or not active or active[-1]['return_id']!=return_id:raise AccountingError('Current revision, first confirmation and latest active return required.')
    target=active[-1];event=OutboxEvent.objects.get(pk=key(POSTED,company.pk,invoice_id,return_id));_,r=verify_post(company,event,body,source)
    if entry_date<r['entry_date']:raise AccountingError('Correction date precedes return.')
    content={'company_id':str(company.pk),'provider_id':str(provider.pk),'invoice_id':invoice_id,'document_id':body['document_id'],'return_id':return_id,'request_id':request_id,'revision':len(entries),'void_index':sum(bool(e.get('reversed')) for e in entries)+1,'history_digest':head,'original_journal_id':source['journal_id'],'original_hash':r['original_hash'],'target_journal_id':target['journal_id'],'target_proof_digest':event.payload['digest'],'reviewed_by':str(user.pk),'entry_date':entry_date,'period_id':period(company,entry_date),'reason_code':reason_code,'evidence_digest':evidence_digest,'selection':r['selection'],'totals':r['totals'],'lines':[{**l,'debit':l['credit'],'credit':l['debit']} for l in r['lines']]}
    row,p=save_review(VOID_REVIEW,company,content);return review_response(company,row,p)

@transaction.atomic
def post_void(*,actor,provider_id,invoice_id,review_id,confirmed):
    user,provider,company,body,source,entries,used,head=context(actor,provider_id,invoice_id);row=OutboxEvent.objects.filter(pk=ledger.identifier(review_id)).first();p=read(row,VOID_REVIEW,company)
    if confirmed is not True or p['reviewed_by']!=str(user.pk) or p['provider_id']!=str(provider.pk) or p['invoice_id']!=invoice_id:raise AccountingError('Second correction confirmation by same owner required.')
    old=next((e for e in entries if e['return_id']==p['return_id'] and e.get('reversed')),None)
    if old:
        proof=OutboxEvent.objects.get(pk=key(VOIDED,company.pk,invoice_id,p['return_id']));v=read(proof,VOIDED,company)
        if v['review_id']!=review_id:raise AccountingError('Correction already used another review.')
        return response(company,invoice_id,body,source,entries,used,head,journal_id=v['journal_id'],replayed=True,ledger_written=True)
    active=[e for e in entries if not e.get('reversed')]
    if not active or active[-1]['return_id']!=p['return_id'] or p['history_digest']!=head or p['revision']!=len(entries) or p['void_index']!=sum(bool(e.get('reversed')) for e in entries)+1 or timezone.now()>=timezone.datetime.fromisoformat(p['expires_at']):raise AccountingError('Correction source/history/expiry changed.')
    journal=write_journal(company,user,p,True);store(VOIDED,company,{'company_id':str(company.pk),'invoice_id':invoice_id,'return_id':p['return_id'],'revision':p['revision'],'void_index':p['void_index'],'original_journal_id':source['journal_id'],'review_id':review_id,'review_digest':fingerprint(p),'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    entries,used,head=history(company,invoice_id,body,source);return response(company,invoice_id,body,source,entries,used,head,journal_id=str(journal.pk),replayed=False,ledger_written=True)

def register_body(company,journal):
    events=list(OutboxEvent.objects.filter(event_type__in=[POSTED,VOIDED],payload__body__company_id=str(company.pk),payload__body__journal_id=str(journal.pk))[:2])
    if len(events)!=1:raise AccountingError('Unique concept return tax origin required.')
    event=events[0];p=read(event,event.event_type,company);r=read(OutboxEvent.objects.filter(pk=p['review_id']).first(),VOID_REVIEW if event.event_type==VOIDED else REVIEW,company);body,source=original(company,r['document_id']);history(company,p['invoice_id'],body,source)
    return {'document_id':body['document_id'],'preview':{'lines':r['lines']}}
