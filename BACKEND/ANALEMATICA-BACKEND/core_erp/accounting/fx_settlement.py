"""Reviewed partial/full monetary settlement against an existing COP cash posting.
No transfer, bank authentication, fee inference, or modification of original journals.
"""
from contextvars import ContextVar
from datetime import date
from decimal import Context, Decimal,localcontext,ROUND_HALF_UP
from uuid import UUID,uuid5
from django.db import transaction
from apps.core_erp.outbox_models import OutboxEvent
from . import reviewed_fx as rates,fx_revaluation as balances
from .models import JournalEntry,LedgerEntry,FiscalPeriod,AccountingEventReceipt
from .validation import lock_company,current_actor,money
from .integrity import fingerprint
from .exceptions import AccountingError
NS=UUID('a3071621-3d25-4672-a7fd-50b6d6099b03')
REVIEW='accounting.fx-settlement.reviewed.v1'
POSTED='accounting.fx-settlement.posted.v1'
CLAIM='accounting.fx-settlement.cash-claimed.v1'
PREFIX='fx-settlement:'
DESCRIPTION='Reviewed monetary FX settlement against recorded cash'
_authorized=ContextVar('fx_settlement_authorized',default=None)
def authorize(company,actor,event):
    if _authorized.get()!=(str(company),str(actor),event):raise AccountingError('Reserved FX settlement requires its explicit reviewed posting command.')
def context(company_id,actor):
    company=lock_company(company_id);user=current_actor(actor)
    if company.currency!='COP' or getattr(user,'is_agent',False):raise AccountingError('Personal COP-book reviewer required.')
    return company,user

def cash_source(company,line_id,clearing_id,as_of,kind,*,current=True):
    line=LedgerEntry.plain_objects.select_related('journal_entry','account__chart_of_accounts').filter(pk=UUID(rates.uid(line_id)),tenant=company,journal_entry__tenant=company,journal_entry__is_posted=True).first()
    if line is None:raise AccountingError('Existing scoped posted cash line required.')
    journal=line.journal_entry
    if journal.is_reversal or journal.hash_version!='v2' or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=1 or journal.date.isoformat()!=as_of or journal.compute_hash()!=journal.system_hash:raise AccountingError('Intact same-day COP cash posting required.')
    rows=list(LedgerEntry.plain_objects.filter(journal_entry=journal).select_related('account__chart_of_accounts').order_by('pk')[:3])
    if len(rows)!=2 or any(r.tenant_id!=company.pk or r.account.tenant_id!=company.pk or r.account.chart_of_accounts.tenant_id!=company.pk or r.currency!='COP' or r.amount_base!=r.debit_amount+r.credit_amount or r.amount_transaction!=r.amount_base for r in rows):raise AccountingError('Two scoped COP cash/clearing lines required; split/fees need separate reviewed handling.')
    other=next((r for r in rows if r.pk!=line.pk),None);receipt=kind=='ASSET'
    if other is None or str(other.account_id)!=clearing_id or line.account_id==other.account_id or line.account.type!='ASSET' or other.account.type!=('LIABILITY' if receipt else 'ASSET') or (line.debit_amount>0)!=receipt or line.debit_amount+line.credit_amount!=other.debit_amount+other.credit_amount or (other.credit_amount>0)!=receipt:raise AccountingError('Recorded receipt/payment and explicit clearing direction do not match monetary account.')
    if current:
        if OutboxEvent.objects.filter(event_type='accounting.reservation.advance-applied.v1',payload__company_id=str(company.pk),payload__allocation__journal_id=str(journal.pk)).exists():raise AccountingError('Recorded cash is already bound to reservation recognition; no cross-domain reuse.')
        from .bank_statement import cash_account
        cash_account(company,str(line.account_id))
        if not other.account.is_active or JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id=journal.pk).exists():raise AccountingError('Active unreversed recorded cash source required.')
    return {'cash_line_id':line_id,'cash_account_id':str(line.account_id),'clearing_account_id':clearing_id,'clearing_line_id':str(other.pk),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'date':as_of,'direction':'IN' if receipt else 'OUT','amount_cop':format(line.debit_amount or line.credit_amount,'.2f')}

def calculation(source,cash,quantity,terms,gain_id,loss_id):
    qty=money(quantity)
    if not isinstance(quantity,str) or format(qty,'.2f')!=quantity:raise AccountingError('Canonical exact foreign quantity required.')
    foreign=Decimal(source['foreign_balance']);carrying=Decimal(source['carrying_cop'])
    if qty<=0 or not foreign or (foreign>0)!=(carrying>0) or qty>abs(foreign):raise AccountingError('Positive partial quantity not exceeding the signed monetary balance required.')
    with localcontext(Context(prec=50)) as ctx:
        ctx.prec=38
        book=abs(carrying) if qty==abs(foreign) else (abs(carrying)*qty/abs(foreign)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
        received=(qty*Decimal(terms['rate'])).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
        money(book);money(received)
        if book<=0 or received<=0 or format(received,'.2f')!=cash['amount_cop']:raise AccountingError('Recorded cash must equal exact quantity times declared rate; no fees or inferred balancing amount.')
        asset=foreign>0;gain=(received-book)*(1 if asset else -1);gain=gain if gain else Decimal('0.00');remaining=abs(foreign)-qty;remaining_cop=abs(carrying)-book
    lines=[{'account_id':source['account_id'],'debit':'0.00' if asset else format(book,'.2f'),'credit':format(book,'.2f') if asset else '0.00'},{'account_id':cash['clearing_account_id'],'debit':format(received,'.2f') if asset else '0.00','credit':'0.00' if asset else format(received,'.2f')}]
    if gain:lines.append({'account_id':gain_id if gain>0 else loss_id,'debit':format(abs(gain),'.2f') if gain<0 else '0.00','credit':format(gain,'.2f') if gain>0 else '0.00'})
    return {'quantity':format(qty,'.2f'),'carrying_released_cop':format(book,'.2f'),'cash_cop':format(received,'.2f'),'realized_difference_cop':format(gain,'.2f'),'foreign_delta':format(-qty if asset else qty,'.2f'),'remaining_foreign':format(remaining if asset or not remaining else -remaining,'.2f'),'remaining_cop':format(remaining_cop if asset or not remaining_cop else -remaining_cop,'.2f'),'rounding':'PROPORTIONAL_CARRYING_HALF_UP_FINAL_REMAINDER','lines':lines}

def read_review(company,row):
    if row is None or row.event_type!=REVIEW or row.domain!='accounting' or row.version!=1 or not isinstance(row.payload,dict):raise AccountingError('FX settlement review unavailable.')
    b=row.payload.get('review')
    if not isinstance(b,dict) or b.get('company_id')!=str(company.pk) or row.aggregate_root!=b['request_id'] or row.pk!=uuid5(NS,'review:'+str(company.pk)+':'+b['request_id']) or row.payload!={'company_id':str(company.pk),'review':b,'digest':fingerprint(b)}:raise AccountingError('FX settlement review changed.')
    rates.quote(b['terms'],{'currency':b['source']['currency'],'date':b['source']['as_of']});rates.quote_record(company,b['terms'])
    if b['calculation']!=calculation(b['source'],b['cash'],b['quantity'],b['terms'],b['gain_account_id'],b['loss_account_id']):raise AccountingError('FX settlement calculation changed.')
    return b

def reversed_journal(company,journal,as_of=None):
    reversals=list(JournalEntry.plain_objects.filter(tenant=company,reversed_entry_id=journal.pk,is_posted=True)[:2])
    if len(reversals)>1:raise AccountingError('Conflicting settlement reversals require reconciliation.')
    if reversals:
        from .ledger_engine import historical_reversal_valuation
        reverse=reversals[0];historical_reversal_valuation(reverse,list(LedgerEntry.plain_objects.filter(journal_entry=reverse).select_related('account')))
        if reverse.compute_hash()!=reverse.system_hash:raise AccountingError('Settlement reversal changed.')
    return bool(reversals) and (as_of is None or reversals[0].date<=date.fromisoformat(as_of))

def proof(company,journal):
    if not journal.financial_event_id or not journal.financial_event_id.startswith(PREFIX):raise AccountingError('Not a reviewed FX settlement origin.')
    review_id=journal.financial_event_id[len(PREFIX):];row=OutboxEvent.objects.filter(pk=UUID(rates.uid(review_id))).first();b=read_review(company,row)
    marker=OutboxEvent.objects.filter(pk=uuid5(NS,'posted:'+review_id)).first();claim=OutboxEvent.objects.filter(pk=uuid5(NS,'claim:'+review_id)).first()
    expected={'company_id':str(company.pk),'review_id':review_id,'review_digest':fingerprint(b),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'cash_line_id':b['cash']['cash_line_id']}
    if marker is None or marker.event_type!=POSTED or marker.domain!='accounting' or marker.version!=1 or marker.aggregate_root!=b['request_id'] or marker.payload!=expected or claim is None or claim.event_type!=CLAIM or claim.domain!='accounting' or claim.version!=1 or claim.aggregate_root!=b['cash']['cash_line_id'] or claim.payload!=expected or journal.is_reversal or not journal.is_posted or journal.hash_version!='v2' or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=1 or journal.date.isoformat()!=b['source']['as_of'] or str(journal.period_id)!=b['period_id'] or str(journal.created_by_id)!=b['reviewed_by'] or journal.compute_hash()!=journal.system_hash:raise AccountingError('FX settlement proof, claim or journal changed.')
    actual=sorted((str(r.account_id),format(r.debit_amount,'.2f'),format(r.credit_amount,'.2f')) for r in LedgerEntry.plain_objects.filter(journal_entry=journal,tenant=company))
    if actual!=sorted((r['account_id'],r['debit'],r['credit']) for r in b['calculation']['lines']):raise AccountingError('FX settlement lines differ from review.')
    contract={'schema':'manual-journal-v2','tenant_id':str(company.pk),'actor_id':journal.created_by_id,'date':b['source']['as_of'],'description':DESCRIPTION,'period_id':b['period_id'],'lines':[{'account':r['account_id'],'debit':r['debit'],'credit':r['credit']} for r in b['calculation']['lines']]}
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=journal.financial_event_id,journal=journal).first()
    if receipt is None or receipt.payload_hash!=fingerprint(contract):raise AccountingError('FX settlement posting receipt changed.')
    kind='ASSET' if Decimal(b['source']['foreign_balance'])>0 else 'LIABILITY'
    if cash_source(company,b['cash']['cash_line_id'],b['cash']['clearing_account_id'],b['source']['as_of'],kind,current=False)!=b['cash']:raise AccountingError('Historical cash source changed.')
    return row,b

def available_cash(company,line_id,as_of):
    journals=list(JournalEntry.plain_objects.filter(tenant=company,is_posted=True,is_reversal=False,financial_event_id__startswith=PREFIX).order_by('pk')[:1001])
    if len(journals)>1000:raise AccountingError('Settlement history exceeds1000; reviewed archival required.')
    seen=[]
    for journal in journals:
        _,body=proof(company,journal);seen.append(str(journal.pk))
        if body['cash']['cash_line_id']==line_id and not reversed_journal(company,journal,as_of):raise AccountingError('Recorded cash line already applied by an active FX settlement.')
    if OutboxEvent.objects.filter(event_type__in=(CLAIM,POSTED),payload__company_id=str(company.pk)).exclude(payload__journal_id__in=seen).exists():raise AccountingError('Orphan FX settlement evidence cannot release cash capacity.')

def current_source(company,b,journal=None):
    try:
        target=balances.account(company,b['source']['account_id'],{'ASSET','LIABILITY'})
        if cash_source(company,b['cash']['cash_line_id'],b['cash']['clearing_account_id'],b['source']['as_of'],target.type)!=b['cash']:return False
        return balances.source(company,b['source']['account_id'],b['source']['currency'],b['source']['as_of'],exclude_journal=journal.pk if journal else None,allow_zero=True)==b['source']
    except (AccountingError,ValueError,TypeError):return False

@transaction.atomic
def review(company_id,*,actor,request_id,account_id,currency,as_of,cash_line_id,clearing_account_id,quantity,terms,gain_account_id,loss_account_id,evidence_digest,monetary_classification,confirmed):
    company,user=context(company_id,actor);rates.uid(request_id)
    from .bank_reconciliation import digest
    digest(evidence_digest)
    if confirmed is not True or monetary_classification!='MONETARY_DECLARED':raise AccountingError('First review and explicit monetary classification required.')
    target=balances.account(company,account_id,{'ASSET','LIABILITY'});balances.account(company,gain_account_id,{'REVENUE'});balances.account(company,loss_account_id,{'EXPENSE'});balances.account(company,clearing_account_id,{'ASSET','LIABILITY'})
    if len({account_id,gain_account_id,loss_account_id,clearing_account_id})!=4:raise AccountingError('Distinct monetary, clearing, gain and loss accounts required.')
    old=OutboxEvent.objects.filter(pk=uuid5(NS,'review:'+str(company.pk)+':'+request_id)).first()
    if old:
        b=read_review(company,old)
        values={'quantity':quantity,'terms':terms,'gain_account_id':gain_account_id,'loss_account_id':loss_account_id,'evidence_digest':evidence_digest,'classification':monetary_classification,'reviewed_by':str(user.pk)}
        if any(b[k]!=v for k,v in values.items()) or any(b['source'][k]!=v for k,v in [('account_id',account_id),('currency',currency),('as_of',as_of)]) or b['cash']['cash_line_id']!=cash_line_id or b['cash']['clearing_account_id']!=clearing_account_id:raise AccountingError('Settlement request identifier reused with changed data.')
        return {'company_id':str(company.pk),'review_id':str(old.pk),'preview':b,'source_current':current_source(company,b),'ledger_written':False,'money_transferred':False,'bank_verified':False,'rate_independently_verified':False}
    source=balances.source(company,account_id,currency,as_of,allow_zero=True)
    if (Decimal(source['foreign_balance'])>0)!=(target.type=='ASSET'):raise AccountingError('Monetary balance sign does not match explicit asset/liability classification.')
    cash=cash_source(company,cash_line_id,clearing_account_id,as_of,target.type)
    if cash['cash_account_id'] in {account_id,gain_account_id,loss_account_id,clearing_account_id}:raise AccountingError('Recorded cash must be a distinct account.')
    available_cash(company,cash_line_id,as_of);terms=rates.quote(terms,{'currency':currency,'date':as_of});rates.quote_record(company,terms,create=True)
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=date.fromisoformat(as_of),period_end__gte=date.fromisoformat(as_of))[:2])
    if len(periods)!=1:raise AccountingError('Exactly one open settlement period required.')
    body={'company_id':str(company.pk),'request_id':request_id,'reviewed_by':str(user.pk),'period_id':str(periods[0].pk),'source':source,'cash':cash,'quantity':quantity,'terms':terms,'gain_account_id':gain_account_id,'loss_account_id':loss_account_id,'evidence_digest':evidence_digest,'classification':monetary_classification,'calculation':calculation(source,cash,quantity,terms,gain_account_id,loss_account_id)}
    row=OutboxEvent.objects.create(id=uuid5(NS,'review:'+str(company.pk)+':'+request_id),event_type=REVIEW,domain='accounting',aggregate_root=request_id,version=1,payload={'company_id':str(company.pk),'review':body,'digest':fingerprint(body)})
    return {'company_id':str(company.pk),'review_id':str(row.pk),'preview':body,'source_current':True,'ledger_written':False,'money_transferred':False,'bank_verified':False,'rate_independently_verified':False}

def outcome(company,user,row,journal,replayed):
    found,b=proof(company,journal)
    if found.pk!=row.pk or b['reviewed_by']!=str(user.pk):raise AccountingError('Settlement belongs to another review/actor.')
    return {'schema':'sgacd-fx-settlement-result-v1','company_id':str(company.pk),'review_id':str(row.pk),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'account_id':b['source']['account_id'],'monetary_kind':'ASSET' if Decimal(b['source']['foreign_balance'])>0 else 'LIABILITY','cash_line_id':b['cash']['cash_line_id'],**{k:b['calculation'][k] for k in ('quantity','carrying_released_cop','cash_cop','realized_difference_cop','remaining_foreign','remaining_cop')},'source_current':current_source(company,b,journal),'original_reversed':reversed_journal(company,journal),'replayed':replayed,'ledger_written':True,'money_transferred':False,'bank_verified':False,'rate_independently_verified':False,'fiscal_accepted':False}

@transaction.atomic
def confirm(company_id,*,actor,review_id,confirmed):
    company,user=context(company_id,actor);row=OutboxEvent.objects.filter(pk=UUID(rates.uid(review_id))).first();b=read_review(company,row)
    if confirmed is not True or b['reviewed_by']!=str(user.pk):raise AccountingError('Second settlement confirmation by the same personal reviewer required.')
    event=PREFIX+review_id;journal=JournalEntry.plain_objects.filter(tenant=company,is_posted=True,financial_event_id=event).first()
    if journal:return outcome(company,user,row,journal,True)
    if OutboxEvent.objects.filter(pk__in=[uuid5(NS,'posted:'+review_id),uuid5(NS,'claim:'+review_id)]).exists() or AccountingEventReceipt.objects.filter(tenant=company,event_id=event).exists():raise AccountingError('Settlement origin conflict; no reconstruction.')
    if not current_source(company,b):raise AccountingError('Monetary balance or cash changed after settlement review.')
    available_cash(company,b['cash']['cash_line_id'],b['source']['as_of'])
    from .ledger_engine import LedgerEngine
    lines=[{'account':balances.account(company,r['account_id'],{'ASSET','LIABILITY','REVENUE','EXPENSE'}),'debit':r['debit'],'credit':r['credit']} for r in b['calculation']['lines']]
    token=_authorized.set((str(company.pk),str(user.pk),event))
    try:journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=date.fromisoformat(b['source']['as_of']),description=DESCRIPTION,lines_data=lines,actor=user,idempotency_key=event,period_id=b['period_id'])
    finally:_authorized.reset(token)
    payload={'company_id':str(company.pk),'review_id':review_id,'review_digest':fingerprint(b),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'cash_line_id':b['cash']['cash_line_id']}
    for prefix,kind,root in [('posted',POSTED,b['request_id']),('claim',CLAIM,b['cash']['cash_line_id'])]:OutboxEvent.objects.create(id=uuid5(NS,prefix+':'+review_id),event_type=kind,domain='accounting',aggregate_root=root,version=1,payload=payload)
    return outcome(company,user,row,journal,False)

@transaction.atomic
def state(company_id,*,actor,review_id):
    company,user=context(company_id,actor);row=OutboxEvent.objects.filter(pk=UUID(rates.uid(review_id))).first();b=read_review(company,row)
    if b['reviewed_by']!=str(user.pk):raise AccountingError('Own settlement review required.')
    journal=JournalEntry.plain_objects.filter(tenant=company,is_posted=True,financial_event_id=PREFIX+review_id).first()
    if journal is None and (OutboxEvent.objects.filter(pk__in=[uuid5(NS,'posted:'+review_id),uuid5(NS,'claim:'+review_id)]).exists() or AccountingEventReceipt.objects.filter(tenant=company,event_id=PREFIX+review_id).exists()):raise AccountingError('Settlement journal missing; no reconstruction.')
    return {'company_id':str(company.pk),'review_id':review_id,'preview':b,'source_current':current_source(company,b,journal),'applied':outcome(company,user,row,journal,True) if journal else None,'read_only':True,'confirmations_restored':False,'ledger_written':False,'money_transferred':False,'bank_verified':False,'rate_independently_verified':False}

@transaction.atomic
def catalog(company_id,*,actor):
    company,user=context(company_id,actor);base=balances.catalog(company.pk,actor=user)
    from . import ratios
    policy=ratios.describe(ratios.latest(company.pk))
    if policy is None:raise AccountingError('Reviewed cash classification required before recorded settlement intake.')
    ratios.normalize(company.pk,policy['mapping'])
    rows=list(LedgerEntry.plain_objects.filter(tenant=company,account_id__in=policy['mapping']['cash_equivalents'],journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__currency='COP',journal_entry__is_reversal=False).select_related('journal_entry').order_by('-journal_entry__date','pk')[:101]);cash=[];excluded=0
    for line in rows[:100]:
        counterparts=list(LedgerEntry.plain_objects.filter(journal_entry=line.journal_entry).exclude(pk=line.pk)[:2])
        if len(counterparts)!=1:excluded+=1;continue
        try:item=cash_source(company,str(line.pk),str(counterparts[0].account_id),line.journal_entry.date.isoformat(),'ASSET' if line.debit_amount>0 else 'LIABILITY')
        except (AccountingError,ValueError,TypeError):excluded+=1;continue
        cash.append(item)
    accounts={**base['accounts'],'clearing':base['accounts']['monetary']}
    return {'schema':'sgacd-fx-settlement-catalog-v1','company_id':str(company.pk),'accounts':accounts,'recorded_cash':cash[:50],'excluded_cash_candidates':excluded,'truncated':base['truncated'] or len(rows)>100 or len(cash)>50,'read_only':True,'ledger_written':False,'money_transferred':False,'bank_verified':False,'rate_independently_verified':False}

def protect_cash_reversal(company,journal):
    originals=list(JournalEntry.plain_objects.filter(tenant=company,is_posted=True,is_reversal=False,financial_event_id__startswith=PREFIX).order_by('pk')[:1001])
    if len(originals)>1000:raise AccountingError('Settlement archival required before reversing a related cash journal.')
    for posted in originals:
        _,b=proof(company,posted)
        if b['cash']['journal_id']==str(journal.pk) and not reversed_journal(company,posted):raise AccountingError('Reverse the active FX settlement before reversing its recorded cash source.')

@transaction.atomic
def request_state(company_id,*,actor,request_id):
    company,user=context(company_id,actor);rates.uid(request_id);row=OutboxEvent.objects.filter(pk=uuid5(NS,'review:'+str(company.pk)+':'+request_id)).first()
    flags={'ledger_written':False,'money_transferred':False,'bank_verified':False,'rate_independently_verified':False,'read_only':True,'confirmations_restored':False}
    if row is None:return {'schema':'sgacd-fx-settlement-request-state-v1','company_id':str(company.pk),'request_id':request_id,'found':False,**flags}
    b=read_review(company,row)
    if b['reviewed_by']!=str(user.pk):raise AccountingError('Own settlement request required.')
    return {'schema':'sgacd-fx-settlement-request-state-v1','company_id':str(company.pk),'request_id':request_id,'found':True,'state':state(company.pk,actor=user,review_id=str(row.pk)),**flags}
