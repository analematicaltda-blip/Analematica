"""Reviewed accrual of declared purchases/sales, input/output tax and withholding.

No invoice issuance, payment, statutory classification or claim of document authenticity.
Public adapters must enforce the existing verified-company owner boundary.
"""
from datetime import date,timedelta
from decimal import Decimal,localcontext
from uuid import UUID,uuid5
import re
from django.db import transaction
from django.utils import timezone
from .validation import lock_company,current_actor
from .exceptions import AccountingError
from .integrity import fingerprint
from .invoice_intent import _money,_format_money
from .models import Account,FiscalPeriod,JournalEntry,LedgerEntry,AccountingEventReceipt
from .ledger_engine import LedgerEngine
from . import tax_policies,source_bindings
from apps.core_erp.outbox_models import OutboxEvent

NS=UUID('89b4cb27-d0b5-43d1-887a-201ed668f593')
REVIEW='accounting.commercial-tax.reviewed.v1'
POSTED='accounting.commercial-tax.posted.v1'
DOCUMENT='accounting.commercial-tax.document-claimed.v1'

def identifier(value):
    if not isinstance(value,str) or str(UUID(value))!=value:raise AccountingError('Canonical document/account identifier required.')
    return value

def digest(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{64}',value):raise AccountingError('Explicit document/evidence SHA-256 required.')
    return value

def root(company,document):return str(company)+':'+document

def event_key(company,document):return 'commercial-tax:'+root(company,document)

def latest(company,document):return OutboxEvent.objects.filter(event_type=REVIEW,aggregate_root=root(company,document),payload__company_id=str(company)).order_by('-payload__revision').first()

def checked(row,kind,company):
    if row is None or row.event_type!=kind or row.domain!='accounting' or row.version!=1 or set(row.payload)!={'company_id','revision','body','digest'}:raise AccountingError('Commercial tax evidence is missing or incompatible.')
    p=row.payload;b=p['body']
    if not isinstance(b,dict) or p['company_id']!=str(company) or b.get('company_id')!=str(company) or p['revision']!=b.get('revision') or fingerprint(b)!=p['digest'] or row.aggregate_root!=root(company,b['document_id']):raise AccountingError('Commercial tax evidence changed.')
    if row.pk!=uuid5(NS,kind+':'+root(company,b['document_id'])+':'+str(b['revision'])):raise AccountingError('Commercial tax evidence identity mismatch.')
    return b

def save(kind,body):
    return OutboxEvent.objects.create(id=uuid5(NS,kind+':'+root(body['company_id'],body['document_id'])+':'+str(body['revision'])),event_type=kind,domain='accounting',aggregate_root=root(body['company_id'],body['document_id']),payload={'company_id':body['company_id'],'revision':body['revision'],'body':body,'digest':fingerprint(body)},version=1)

def preview(company,fact):
    fields={'document_id','document_digest','counterparty_id','direction','entry_date','items','settlement_account_id'}
    if not isinstance(fact,dict) or set(fact)!=fields or fact['direction'] not in {'PURCHASE','SALE'} or company.currency!='COP':raise AccountingError('Explicit supported COP purchase/sale fact required.')
    for field in ['document_id','counterparty_id','settlement_account_id']:identifier(fact[field])
    digest(fact['document_digest']);day=date.fromisoformat(fact['entry_date'])
    if day.isoformat()!=fact['entry_date'] or day>timezone.localdate():raise AccountingError('Canonical nonfuture economic date required.')
    if not isinstance(fact['items'],list) or not 1<=len(fact['items'])<=20:raise AccountingError('One to20 reviewed components required.')
    purchase=fact['direction']=='PURCHASE';lines=[];quotes=[];net_total=tax_total=ret_total=0;seen=set()
    def account(pk,types):
        identifier(pk)
        row=Account.plain_objects.select_related('chart_of_accounts').filter(pk=pk,tenant_id=company.pk,is_active=True,type__in=types,chart_of_accounts__tenant_id=company.pk).first()
        if row is None:raise AccountingError('Account is foreign, inactive or incompatible with its explicit role.')
        return row
    settlement=account(fact['settlement_account_id'],{'LIABILITY'} if purchase else {'ASSET'})
    def line(pk,amount,debit,kind):
        if amount:lines.append({'account_id':pk,'debit':_format_money(amount if debit else 0),'credit':_format_money(0 if debit else amount),'kind':kind})
    for item in fact['items']:
        if not isinstance(item,dict) or set(item)!={'item_id','net','tax_category','policy_code','policy_revision','basis_account_id','tax_accounts'}:raise AccountingError('Invalid reviewed item contract.')
        identifier(item['item_id'])
        if item['item_id'] in seen:raise AccountingError('Duplicate component identity.')
        seen.add(item['item_id']);net=_money(item['net'])
        if net<=0 or item['tax_category'] not in tax_policies.CATEGORIES or type(item['policy_revision']) is not int or item['policy_revision']<1 or not isinstance(item['policy_code'],str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,39}',item['policy_code']):raise AccountingError('Positive exact net, category and policy version required.')
        policy=tax_policies.versions(company.pk,item['policy_code']).filter(payload__revision=item['policy_revision']).first()
        if policy is None:raise AccountingError('Recorded company policy required.')
        terms=tax_policies.verified(policy,company.pk)['terms']
        if not terms['valid_from']<=fact['entry_date']<=terms['valid_until']:raise AccountingError('Selected policy is not valid on the economic date.')
        basis=account(item['basis_account_id'],{'EXPENSE','ASSET'} if purchase else {'REVENUE'})
        if basis.pk==settlement.pk:raise AccountingError('Basis and settlement roles must be distinct.')
        line(str(basis.pk),net,purchase,'BASIS');tax=ret=0;components=[];required=set()
        if not isinstance(item['tax_accounts'],dict):raise AccountingError('Explicit tax accounts required.')
        for rule in terms['components']:
            applied=item['tax_category'] in rule['applies_to'];amount=(net*rule['rate_bps']+5000)//10000 if applied else 0
            if amount:
                if rule['kind'] not in ({'INPUT_TAX','WITHHOLDING'} if purchase else {'OUTPUT_TAX','WITHHOLDING'}):raise AccountingError('Input/output policy incompatible with purchase/sale; no implicit tax reclassification.')
                required.add(rule['code'])
                if rule['code'] not in item['tax_accounts']:raise AccountingError('Missing component tax account.')
                kind='ASSET' if (purchase and rule['kind']=='INPUT_TAX') or (not purchase and rule['kind']=='WITHHOLDING') else 'LIABILITY'
                target=account(item['tax_accounts'][rule['code']],{kind})
                if target.pk in {basis.pk,settlement.pk}:raise AccountingError('Tax and commercial roles must be distinct.')
                debit=rule['kind']!='WITHHOLDING' if purchase else rule['kind']=='WITHHOLDING'
                line(str(target.pk),amount,debit,rule['kind'])
            if rule['kind']=='WITHHOLDING':ret+=amount
            else:tax+=amount
            components.append({'code':rule['code'],'kind':rule['kind'],'basis':_format_money(net),'rate_bps':rule['rate_bps'],'applied':applied,'amount':_format_money(amount)})
        if set(item['tax_accounts'])!=required:raise AccountingError('Tax account mapping must match positive applied components exactly.')
        if ret>net+tax:raise AccountingError('Withholding exceeds gross amount.')
        quotes.append({'item_id':item['item_id'],'policy_id':str(policy.pk),'policy_digest':policy.payload['policy_digest'],'components':components});net_total+=net;tax_total+=tax;ret_total+=ret
    line(str(settlement.pk),net_total+tax_total-ret_total,not purchase,'SETTLEMENT')
    if len(lines)<2:raise AccountingError('Balanced commercial lines required.')
    # Bound duplicate account roles across components by economic side.
    sides={}
    for row in lines:
        side=row['debit']!='0.00'
        if row['account_id'] in sides and sides[row['account_id']]!=side:raise AccountingError('An account cannot net incompatible commercial roles.')
        sides[row['account_id']]=side
    return {'company_id':str(company.pk),'currency':'COP','quotes':quotes,'lines':lines,'totals':{'net':_format_money(net_total),'tax':_format_money(tax_total),'withholding':_format_money(ret_total),'gross':_format_money(net_total+tax_total),'settlement':_format_money(net_total+tax_total-ret_total)},'regulatory_verified':False,'source_independently_verified':False}

@transaction.atomic
def review_fact(company_id,*,actor,fact,evidence_digest,expected_revision,confirmed,source_binding=None):
    company=lock_company(company_id);user=current_actor(actor)
    if confirmed is not True or type(expected_revision) is not int or expected_revision<0:raise AccountingError('Explicit first confirmation and revision required.')
    digest(evidence_digest);calculated=preview(company,fact);doc=fact['document_id']
    source_bindings.require(company.pk,doc,source_binding,user.pk,'REVIEW',fact['document_digest'])
    if OutboxEvent.objects.filter(event_type=POSTED,aggregate_root=root(company.pk,doc)).exists():raise AccountingError('Document already posted; adjust by a reviewed reversal, never overwrite.')
    if OutboxEvent.objects.filter(pk=uuid5(NS,'document:'+str(company.pk)+':'+fact['document_digest'])).exists():raise AccountingError('This document digest has already been claimed.')
    old=latest(company.pk,doc);revision=checked(old,REVIEW,company.pk)['revision'] if old else 0
    if revision!=expected_revision:raise AccountingError('Review revision changed.')
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=fact['entry_date'],period_end__gte=fact['entry_date'])[:2])
    if len(periods)!=1:raise AccountingError('Exactly one open period required.')
    now=timezone.now();body={'company_id':str(company.pk),'document_id':doc,'revision':revision+1,'reviewed_by':str(user.pk),'fact':fact,'preview':calculated,'evidence_digest':evidence_digest,'period_id':str(periods[0].pk),'expires_at':(now+timedelta(minutes=15)).isoformat(),'source_kind':'MANUAL_REVIEWED_FACT'}
    if source_binding is not None:body['source_binding']=source_binding
    row=save(REVIEW,body)
    return {'company_id':str(company.pk),'review_id':str(row.pk),'preview':calculated,'revision':body['revision'],'ledger_written':False,'regulatory_verified':False,'money_transferred':False}

def validate_posted_snapshot(company,review,body,proof,journal,receipt,claim,lines):
    """Shared pure validation for single results and a locked, bulk-read register."""
    from .integrity import journal_hash
    posted=checked(proof,POSTED,company.pk)
    if posted['review_id']!=str(review.pk) or posted['review_digest']!=fingerprint(body):raise AccountingError('Posting/review link changed.')
    expected_claim={'company_id':str(company.pk),'document_id':body['document_id'],'document_digest':body['fact']['document_digest'],'journal_id':posted['journal_id']}
    if journal is None or str(journal.pk)!=posted['journal_id'] or journal.tenant_id!=company.pk or not journal.is_posted or journal.is_reversal or journal.financial_event_id!=event_key(company.pk,body['document_id']) or receipt is None or receipt.journal_id!=journal.pk or receipt.tenant_id!=company.pk or receipt.event_id!=event_key(company.pk,body['document_id']) or claim is None or claim.event_type!=DOCUMENT or claim.domain!='accounting' or claim.aggregate_root!=root(company.pk,body['document_id']) or claim.payload!=expected_claim:raise AccountingError('Posted journal, receipt or document proof requires reconciliation.')
    if journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=Decimal('1') or journal.hash_version!='v2' or journal.date.isoformat()!=body['fact']['entry_date'] or str(journal.period_id)!=body['period_id'] or str(journal.created_by_id)!=body['reviewed_by']:raise AccountingError('Posted journal context changed.')
    if journal_hash(journal,lines,journal.previous_hash or 'GENESIS_SARITA_2026')!=posted['journal_hash'] or journal.system_hash!=posted['journal_hash']:raise AccountingError('Posted journal hash requires reconciliation.')
    if any(l.tenant_id!=company.pk or l.account.tenant_id!=company.pk or l.journal_entry_id!=journal.pk or l.currency!='COP' or l.amount_base!=l.debit_amount+l.credit_amount or l.amount_transaction!=l.debit_amount+l.credit_amount for l in lines):raise AccountingError('Posted line scope or valuation changed.')
    contract={'schema':'manual-journal-v2','tenant_id':str(company.pk),'actor_id':journal.created_by_id,'date':body['fact']['entry_date'],'description':'Reviewed commercial '+body['fact']['direction'],'period_id':body['period_id'],'lines':[{'account':x['account_id'],'debit':x['debit'],'credit':x['credit']} for x in body['preview']['lines']]}
    if receipt.payload_hash!=fingerprint(contract):raise AccountingError('Posting receipt does not match the reviewed contract.')
    actual=sorted((str(x.account_id),format(x.debit_amount,'.2f'),format(x.credit_amount,'.2f')) for x in lines)
    expected=sorted((x['account_id'],x['debit'],x['credit']) for x in body['preview']['lines'])
    if actual!=expected:raise AccountingError('Posted lines differ from the reviewed components.')

def posted_state(company,review,body,proof):
    posted=checked(proof,POSTED,company.pk)
    journal=JournalEntry.plain_objects.filter(pk=posted['journal_id'],tenant_id=company.pk).first()
    receipt=AccountingEventReceipt.objects.filter(tenant_id=company.pk,event_id=event_key(company.pk,body['document_id'])).first()
    claim=OutboxEvent.objects.filter(pk=uuid5(NS,'document:'+str(company.pk)+':'+body['fact']['document_digest'])).first()
    lines=list(LedgerEntry.plain_objects.filter(journal_entry_id=posted['journal_id'],tenant_id=company.pk).select_related('account'))
    validate_posted_snapshot(company,review,body,proof,journal,receipt,claim,lines)
    return {'company_id':str(company.pk),'document_id':body['document_id'],'journal_id':str(journal.pk),'ledger_written':True,'reversed':JournalEntry.plain_objects.filter(tenant_id=company.pk,is_posted=True,reversed_entry_id=journal.pk).exists(),'regulatory_verified':False,'money_transferred':False,'fiscal_document_created':False}

@transaction.atomic
def post_fact(company_id,*,actor,document_id,review_id,confirmed):
    company=lock_company(company_id);user=current_actor(actor);identifier(document_id)
    if confirmed is not True:raise AccountingError('Second explicit confirmation required.')
    review=latest(company.pk,document_id);body=checked(review,REVIEW,company.pk)
    if str(review.pk)!=identifier(review_id) or body['reviewed_by']!=str(user.pk):raise AccountingError('Current review by this owner required.')
    source_bindings.require(company.pk,document_id,body.get('source_binding'),user.pk,'POST',body['fact']['document_digest'])
    proof=OutboxEvent.objects.filter(pk=uuid5(NS,POSTED+':'+root(company.pk,document_id)+':'+str(body['revision']))).first()
    if proof:return {**posted_state(company,review,body,proof),'replayed':True}
    if AccountingEventReceipt.objects.filter(tenant=company,event_id=event_key(company.pk,document_id)).exists() or JournalEntry.plain_objects.filter(tenant=company,financial_event_id=event_key(company.pk,document_id)).exists():raise AccountingError('Missing origin proof; no reconstruction or second posting.')
    if timezone.now()>=timezone.datetime.fromisoformat(body['expires_at']) or preview(company,body['fact'])!=body['preview']:raise AccountingError('Expired or changed review; review current data again.')
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=body['fact']['entry_date'],period_end__gte=body['fact']['entry_date'])[:2])
    if len(periods)!=1 or str(periods[0].pk)!=body['period_id']:raise AccountingError('Accounting period changed.')
    claim_id=uuid5(NS,'document:'+str(company.pk)+':'+body['fact']['document_digest'])
    if OutboxEvent.objects.filter(pk=claim_id).exists():raise AccountingError('Document digest already claimed.')
    lines=[{'account':Account.plain_objects.get(pk=x['account_id'],tenant=company),'debit':x['debit'],'credit':x['credit']} for x in body['preview']['lines']]
    with localcontext() as ctx:
        ctx.prec=38
        journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=date.fromisoformat(body['fact']['entry_date']),description='Reviewed commercial '+body['fact']['direction'],lines_data=lines,actor=user,idempotency_key=event_key(company.pk,document_id),period_id=body['period_id'])
    save(POSTED,{'company_id':str(company.pk),'document_id':document_id,'revision':body['revision'],'review_id':str(review.pk),'review_digest':fingerprint(body),'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    OutboxEvent.objects.create(id=claim_id,event_type=DOCUMENT,domain='accounting',aggregate_root=root(company.pk,document_id),payload={'company_id':str(company.pk),'document_id':document_id,'document_digest':body['fact']['document_digest'],'journal_id':str(journal.pk)},version=1)
    return {**posted_state(company,review,body,OutboxEvent.objects.get(pk=uuid5(NS,POSTED+':'+root(company.pk,document_id)+':'+str(body['revision'])))),'replayed':False}

@transaction.atomic
def fact_state(company_id,*,actor,document_id):
    company=lock_company(company_id);current_actor(actor);identifier(document_id);row=latest(company.pk,document_id)
    if row is None:return {'company_id':str(company.pk),'document_id':document_id,'review':None,'posted':None,'read_only':True,'confirmations_restored':False}
    body=checked(row,REVIEW,company.pk);proof=OutboxEvent.objects.filter(pk=uuid5(NS,POSTED+':'+root(company.pk,document_id)+':'+str(body['revision']))).first()
    return {'company_id':str(company.pk),'document_id':document_id,'review':{'review_id':str(row.pk),'revision':body['revision'],'preview':body['preview'],'expires_at':body['expires_at']},'posted':posted_state(company,row,body,proof) if proof else None,'read_only':True,'confirmations_restored':False}

REV_REVIEW='accounting.commercial-tax.reversal-reviewed.v1'
REVERSED='accounting.commercial-tax.reversed.v1'

def original_state(company,document):
    review=latest(company.pk,document);body=checked(review,REVIEW,company.pk)
    proof=OutboxEvent.objects.filter(pk=uuid5(NS,POSTED+':'+root(company.pk,document)+':'+str(body['revision']))).first()
    return review,body,proof,posted_state(company,review,body,proof)

@transaction.atomic
def review_reversal(company_id,*,actor,document_id,reason_code,evidence_digest,confirmed):
    company=lock_company(company_id);user=current_actor(actor);identifier(document_id);digest(evidence_digest)
    if confirmed is not True or not isinstance(reason_code,str) or not re.fullmatch('[A-Z0-9_-]{1,40}',reason_code):raise AccountingError('Explicit reversal reason code and first confirmation required.')
    original,body,proof,state=original_state(company,document_id)
    source_bindings.require(company.pk,document_id,body.get('source_binding'),user.pk,'REVERSE_REVIEW',body['fact']['document_digest'])
    if state['reversed']:raise AccountingError('Original is already reversed; no second adjustment.')
    old=OutboxEvent.objects.filter(event_type=REV_REVIEW,aggregate_root=root(company.pk,document_id)).order_by('-payload__revision').first()
    revision=checked(old,REV_REVIEW,company.pk)['revision'] if old else 0
    content={'company_id':str(company.pk),'document_id':document_id,'revision':revision+1,'reviewed_by':str(user.pk),'original_review_id':str(original.pk),'original_proof_digest':proof.payload['digest'],'original_journal_id':state['journal_id'],'reason_code':reason_code,'evidence_digest':evidence_digest,'expires_at':(timezone.now()+timedelta(minutes=15)).isoformat()}
    row=save(REV_REVIEW,content)
    return {'company_id':str(company.pk),'document_id':document_id,'review_id':str(row.pk),'original_journal_id':state['journal_id'],'ledger_written':False,'regulatory_verified':False,'money_transferred':False}

@transaction.atomic
def reverse_fact(company_id,*,actor,document_id,review_id,confirmed):
    company=lock_company(company_id);user=current_actor(actor);identifier(document_id)
    if confirmed is not True:raise AccountingError('Second reversal confirmation required.')
    row=OutboxEvent.objects.filter(event_type=REV_REVIEW,aggregate_root=root(company.pk,document_id)).order_by('-payload__revision').first();body=checked(row,REV_REVIEW,company.pk)
    if identifier(review_id)!=str(row.pk) or str(user.pk)!=body['reviewed_by']:raise AccountingError('Current reversal review by this owner required.')
    original,source,proof,state=original_state(company,document_id)
    source_bindings.require(company.pk,document_id,source.get('source_binding'),user.pk,'REVERSE_POST',source['fact']['document_digest'])
    if body['original_review_id']!=str(original.pk) or body['original_proof_digest']!=proof.payload['digest'] or body['original_journal_id']!=state['journal_id']:raise AccountingError('Original posting changed after review.')
    prior=OutboxEvent.objects.filter(pk=uuid5(NS,REVERSED+':'+root(company.pk,document_id)+':'+str(body['revision']))).first()
    if prior:
        result=checked(prior,REVERSED,company.pk)
        if result['review_id']!=str(row.pk) or result['review_digest']!=fingerprint(body):raise AccountingError('Reversal review proof changed.')
        journal=JournalEntry.plain_objects.filter(pk=result['journal_id'],tenant=company,is_posted=True,is_reversal=True,reversed_entry_id=body['original_journal_id']).first()
        if journal is None or journal.system_hash!=result['journal_hash'] or journal.compute_hash()!=result['journal_hash']:raise AccountingError('Reversal integrity requires reconciliation.')
        expected=sorted((x['account_id'],x['credit'],x['debit']) for x in source['preview']['lines'])
        actual=sorted((str(x.account_id),format(x.debit_amount,'.2f'),format(x.credit_amount,'.2f')) for x in LedgerEntry.plain_objects.filter(journal_entry=journal,tenant=company))
        if actual!=expected:raise AccountingError('Reversal lines differ from the original contra entries.')
        return {'company_id':str(company.pk),'document_id':document_id,'journal_id':str(journal.pk),'original_journal_id':state['journal_id'],'replayed':True,'ledger_written':True,'regulatory_verified':False,'money_transferred':False,'fiscal_document_created':False}
    if state['reversed']:raise AccountingError('Unlinked reversal requires reconciliation; no reconstruction.')
    if timezone.now()>=timezone.datetime.fromisoformat(body['expires_at']):raise AccountingError('Reversal review expired.')
    journal=LedgerEngine.reverse_entry(body['original_journal_id'],reason='Reviewed commercial reversal '+body['reason_code'],tenant_id=company.pk,actor=user)
    save(REVERSED,{'company_id':str(company.pk),'document_id':document_id,'revision':body['revision'],'review_id':str(row.pk),'review_digest':fingerprint(body),'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    return {'company_id':str(company.pk),'document_id':document_id,'journal_id':str(journal.pk),'original_journal_id':state['journal_id'],'replayed':False,'ledger_written':True,'regulatory_verified':False,'money_transferred':False,'fiscal_document_created':False}
