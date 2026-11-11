"""Reviewed monetary account true-up from the posted ledger; no realized FX or payment.
Dedicated USD/EUR monetary accounts only. Unknown COP/legacy balances fail closed.
"""
from datetime import date
from decimal import Decimal,ROUND_HALF_UP,localcontext
from uuid import UUID,uuid5
from django.db import transaction
from django.utils import timezone
from apps.core_erp.outbox_models import OutboxEvent
from . import reviewed_fx as rates
from .exceptions import AccountingError
from .integrity import fingerprint
from .models import Account,JournalEntry,LedgerEntry,FiscalPeriod,AccountingEventReceipt
from .validation import lock_company,current_actor,money
NS=UUID('a89b8a21-7cdb-486b-8cc5-4652c86d071c')
REVIEW='accounting.fx-balance.reviewed.v1'
POSTED='accounting.fx-balance.posted.v1'
PREFIX='fx-revaluation:'

def account(company,identifier,kinds):
    row=Account.plain_objects.select_for_update().select_related('chart_of_accounts').filter(pk=UUID(rates.uid(identifier)),tenant=company,is_active=True,type__in=kinds).first()
    if row is None or row.chart_of_accounts.tenant_id!=company.pk:raise AccountingError('Own active monetary/gain/loss account required.')
    return row

def calculation(snapshot,terms,gain_id,loss_id):
    with localcontext() as ctx:
        ctx.prec=38
        desired=(Decimal(snapshot['foreign_balance'])*Decimal(terms['rate'])).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
        delta=desired-Decimal(snapshot['carrying_cop']);money(abs(desired));money(abs(delta))
    if not delta:raise AccountingError('No FX difference exists; no zero journal is created.')
    target=snapshot['account_id'];counter=gain_id if delta>0 else loss_id;value=format(abs(delta),'.2f')
    return {'desired_cop':format(desired,'.2f'),'difference_cop':format(delta,'.2f'),'rounding':'BALANCE_HALF_UP','lines':[{'account_id':target,'debit':value if delta>0 else '0.00','credit':value if delta<0 else '0.00'},{'account_id':counter,'debit':value if delta<0 else '0.00','credit':value if delta>0 else '0.00'}]}

def read_review(company,row):
    if row is None or row.event_type!=REVIEW or row.domain!='accounting' or row.version!=1:raise AccountingError('FX balance review unavailable.')
    body=row.payload.get('review')
    if not isinstance(body,dict) or body.get('company_id')!=str(company.pk) or row.payload!= {'company_id':str(company.pk),'review':body,'digest':fingerprint(body)} or row.aggregate_root!=body['request_id'] or row.pk!=uuid5(NS,'review:'+str(company.pk)+':'+body['request_id']):raise AccountingError('FX balance review changed.')
    rates.quote(body['terms'],{'currency':body['source']['currency'],'date':body['source']['as_of']});rates.quote_record(company,body['terms'])
    if body['calculation']!=calculation(body['source'],body['terms'],body['gain_account_id'],body['loss_account_id']):raise AccountingError('FX balance calculation changed.')
    return body

def proof(company,journal):
    if not journal.financial_event_id or not journal.financial_event_id.startswith(PREFIX):raise AccountingError('Not a reviewed FX balance origin.')
    review_id=journal.financial_event_id[len(PREFIX):];row=OutboxEvent.objects.filter(pk=UUID(rates.uid(review_id))).first();body=read_review(company,row)
    marker=OutboxEvent.objects.filter(pk=uuid5(NS,'posted:'+review_id)).first()
    expected={'company_id':str(company.pk),'review_id':review_id,'review_digest':fingerprint(body),'journal_id':str(journal.pk),'journal_hash':journal.system_hash}
    if marker is None or marker.event_type!=POSTED or marker.domain!='accounting' or marker.version!=1 or marker.aggregate_root!=body['request_id'] or marker.payload!=expected or not journal.is_posted or journal.is_reversal or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=Decimal(1) or journal.hash_version!='v2' or journal.compute_hash()!=journal.system_hash or journal.date.isoformat()!=body['source']['as_of'] or str(journal.period_id)!=body['period_id'] or str(journal.created_by_id)!=body['reviewed_by']:raise AccountingError('FX balance origin proof missing or changed.')
    actual=sorted((str(r.account_id),format(r.debit_amount,'.2f'),format(r.credit_amount,'.2f')) for r in LedgerEntry.plain_objects.filter(journal_entry=journal,tenant=company))
    if actual!=sorted((r['account_id'],r['debit'],r['credit']) for r in body['calculation']['lines']):raise AccountingError('FX balance lines differ from review.')
    contract={'schema':'manual-journal-v2','tenant_id':str(company.pk),'actor_id':journal.created_by_id,'date':body['source']['as_of'],'description':'Reviewed monetary FX revaluation','period_id':body['period_id'],'lines':[{'account':r['account_id'],'debit':r['debit'],'credit':r['credit']} for r in body['calculation']['lines']]}
    receipt=AccountingEventReceipt.objects.filter(tenant=company,event_id=journal.financial_event_id,journal=journal).first()
    if receipt is None or receipt.payload_hash!=fingerprint(contract):raise AccountingError('FX balance posting receipt changed.')
    return row,body

def source(company,account_id,currency,as_of,exclude_journal=None,allow_zero=False):
    target=account(company,account_id,{'ASSET','LIABILITY'})
    if company.currency!='COP' or currency not in {'USD','EUR'} or target.initial_balance!=0:raise AccountingError('Dedicated USD/EUR monetary account with ledger-backed opening required.')
    from apps.core_erp.fx.models import Currency
    if Currency.objects.filter(code__in=[currency,'COP'],is_active=True).count()!=2:raise AccountingError('Active currency pair required.')
    day=date.fromisoformat(as_of)
    if day.isoformat()!=as_of or day>timezone.localdate():raise AccountingError('Canonical nonfuture FX economic date required.')
    if JournalEntry.plain_objects.filter(tenant=company,is_posted=True,date__gt=day,financial_event_id__startswith=PREFIX,lines__account=target).exists():raise AccountingError('A later FX revaluation exists; backdated adjustment requires reviewed reconciliation.')
    if JournalEntry.plain_objects.filter(tenant=company,is_posted=True,date__gt=day,financial_event_id__startswith='fx-settlement:',lines__account=target).exists():raise AccountingError('A later FX settlement exists; no backdated balance inference.')
    for origin_prefix in ('fx-settlement:','fx-revaluation:','reviewed-fx:'):
        if JournalEntry.plain_objects.filter(tenant=company,is_posted=True,is_reversal=True,date__gt=day,reversed_entry_id__in=JournalEntry.plain_objects.filter(tenant=company,financial_event_id__startswith=origin_prefix).values('pk'),lines__account=target).exists():raise AccountingError('A later monetary reversal exists; no backdated settlement/revaluation.')
    query=LedgerEntry.plain_objects.filter(account=target,tenant=company,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__date__lte=day)
    if exclude_journal:query=query.exclude(journal_entry_id=exclude_journal)
    rows=list(query.select_related('journal_entry').order_by('pk')[:51])
    if not rows or len(rows)>50:raise AccountingError('One to50 posted monetary lines supported; reviewed archival/batches required above that limit.')
    foreign=carrying=Decimal('0.00');records=[];validated=set()
    with localcontext() as ctx:
        ctx.prec=38
        for line in rows:
            settlement_record={}
            journal=line.journal_entry;amount=line.debit_amount or line.credit_amount;sign=1 if line.debit_amount>0 else -1
            if journal.pk not in validated:
                if journal.hash_version!='v2' or journal.base_currency!='COP' or journal.compute_hash()!=journal.system_hash:raise AccountingError('Every monetary source journal must have intact v2 COP valuation.')
                validated.add(journal.pk)
            if line.currency!=journal.currency or line.amount_transaction!=amount:raise AccountingError('Monetary transaction currency/amount changed.')
            if line.currency==currency:
                if journal.is_reversal:
                    from .ledger_engine import historical_reversal_valuation
                    historical_reversal_valuation(journal,list(LedgerEntry.plain_objects.filter(journal_entry=journal).select_related('account')))
                elif (target.type=='ASSET' and sign<0) or (target.type=='LIABILITY' and sign>0):raise AccountingError('Partial settlement/consumption needs a realized-FX reconciliation; it is not inferred as revaluation.')
                if journal.financial_event_id and journal.financial_event_id.startswith('reviewed-fx:'):rates.verify_posted_origin(company,journal.created_by,journal)
                expected=(amount*journal.exchange_rate).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
                if line.amount_base!=expected:raise AccountingError('Recorded monetary base differs from historical rate.')
                foreign+=amount*sign
            elif line.currency=='COP':
                original=journal
                if journal.is_reversal:
                    original=JournalEntry.plain_objects.filter(pk=journal.reversed_entry_id,tenant=company,is_posted=True).first()
                    if original is None:raise AccountingError('FX contra origin missing.')
                    from .ledger_engine import historical_reversal_valuation
                    historical_reversal_valuation(journal,list(LedgerEntry.plain_objects.filter(journal_entry=journal).select_related('account')))
                if original.financial_event_id and original.financial_event_id.startswith('fx-settlement:'):
                    from . import fx_settlement as settlement
                    sr,origin=settlement.proof(company,original)
                    delta=Decimal(origin['calculation']['foreign_delta'])*(-1 if journal.is_reversal else 1)
                    foreign+=delta
                    settlement_record={'foreign_delta':format(delta,'.2f'),'settlement_review_id':str(sr.pk),'settlement_proof_digest':fingerprint(origin)}
                    if not settlement.reversed_journal(company,original,as_of) and JournalEntry.plain_objects.filter(tenant=company,is_posted=True,date__lte=day,reversed_entry_id=origin['cash']['journal_id']).exists():raise AccountingError('Active settlement lost its recorded cash source; reconcile before valuing.')
                else:_,origin=proof(company,original)
                if origin['source']['account_id']!=account_id or origin['source']['currency']!=currency or line.amount_base!=amount:raise AccountingError('Unexplained COP movement in monetary account.')
            else:raise AccountingError('Mixed foreign currencies require separate monetary accounts.')
            carrying+=line.amount_base*sign
            records.append({'line_id':str(line.pk),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'date':journal.date.isoformat(),'currency':line.currency,'debit':format(line.debit_amount,'.2f'),'credit':format(line.credit_amount,'.2f'),'amount_base':format(line.amount_base,'.2f'),'rate':format(journal.exchange_rate,'.6f'),**settlement_record})
    if not foreign and (not allow_zero or carrying):raise AccountingError('No remaining foreign balance; residual COP requires settlement/contra reconciliation.')
    return {'account_id':account_id,'currency':currency,'as_of':as_of,'foreign_balance':format(foreign,'.2f'),'carrying_cop':format(carrying,'.2f'),'records':records}

@transaction.atomic
def review(company_id,*,actor,request_id,account_id,currency,as_of,terms,gain_account_id,loss_account_id,monetary_classification,confirmed):
    company=lock_company(company_id);user=current_actor(actor);rates.uid(request_id)
    if confirmed is not True or monetary_classification!='MONETARY_DECLARED':raise AccountingError('First explicit review and professional monetary classification declaration required.')
    gain=account(company,gain_account_id,{'REVENUE'});loss=account(company,loss_account_id,{'EXPENSE'})
    if len({account_id,gain_account_id,loss_account_id})!=3:raise AccountingError('Three distinct monetary/gain/loss accounts required.')
    snapshot=source(company,account_id,currency,as_of);terms=rates.quote(terms,{'currency':currency,'date':as_of});rates.quote_record(company,terms,create=True)
    periods=list(FiscalPeriod.plain_objects.filter(tenant=company,status='open',period_start__lte=date.fromisoformat(as_of),period_end__gte=date.fromisoformat(as_of))[:2])
    if len(periods)!=1:raise AccountingError('Exactly one open FX adjustment period required.')
    body={'company_id':str(company.pk),'request_id':request_id,'reviewed_by':str(user.pk),'period_id':str(periods[0].pk),'source':snapshot,'terms':terms,'gain_account_id':str(gain.pk),'loss_account_id':str(loss.pk),'classification':monetary_classification,'classification_independently_verified':False,'calculation':calculation(snapshot,terms,gain_account_id,loss_account_id)}
    identifier=uuid5(NS,'review:'+str(company.pk)+':'+request_id);existing=OutboxEvent.objects.filter(pk=identifier).first()
    if existing:
        if read_review(company,existing)!=body:raise AccountingError('FX request identifier reused with changed source/terms.')
        row=existing
    else:row=OutboxEvent.objects.create(id=identifier,event_type=REVIEW,domain='accounting',aggregate_root=request_id,version=1,payload={'company_id':str(company.pk),'review':body,'digest':fingerprint(body)})
    return {'company_id':str(company.pk),'review_id':str(row.pk),'preview':body,'ledger_written':False,'money_transferred':False,'rate_independently_verified':False}

def outcome(company,user,row,journal,replayed):
    checked,body=proof(company,journal)
    if checked.pk!=row.pk or body['reviewed_by']!=str(user.pk):raise AccountingError('FX revaluation belongs to another owner/review.')
    try:current=source(company,body['source']['account_id'],body['source']['currency'],body['source']['as_of'],exclude_journal=journal.pk)==body['source']
    except (AccountingError,ValueError,TypeError):current=False
    reverse=list(JournalEntry.plain_objects.filter(tenant=company,reversed_entry_id=journal.pk,is_posted=True)[:2])
    if len(reverse)>1 or any(r.compute_hash()!=r.system_hash for r in reverse):raise AccountingError('FX revaluation contra integrity changed.')
    return {'schema':'sgacd-fx-revaluation-result-v1','company_id':str(company.pk),'review_id':str(row.pk),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'account_id':body['source']['account_id'],'foreign_balance':body['source']['foreign_balance'],'carrying_cop':body['source']['carrying_cop'],'desired_cop':body['calculation']['desired_cop'],'difference_cop':body['calculation']['difference_cop'],'source_current':current,'original_reversed':bool(reverse),'replayed':replayed,'ledger_written':True,'money_transferred':False,'rate_independently_verified':False,'fiscal_accepted':False}

@transaction.atomic
def confirm(company_id,*,actor,review_id,confirmed):
    company=lock_company(company_id);user=current_actor(actor);row=OutboxEvent.objects.filter(pk=UUID(rates.uid(review_id))).first();body=read_review(company,row)
    if confirmed is not True or body['reviewed_by']!=str(user.pk):raise AccountingError('Second confirmation by same FX reviewer required.')
    event_id=PREFIX+review_id;journal=JournalEntry.plain_objects.filter(tenant=company,financial_event_id=event_id,is_posted=True).first()
    if journal:return outcome(company,user,row,journal,True)
    if OutboxEvent.objects.filter(pk=uuid5(NS,'posted:'+review_id)).exists() or AccountingEventReceipt.objects.filter(tenant=company,event_id=event_id).exists():raise AccountingError('FX proof/journal origin conflict; no reconstruction.')
    if source(company,body['source']['account_id'],body['source']['currency'],body['source']['as_of'])!=body['source']:raise AccountingError('Monetary source changed since review; review again.')
    gain=account(company,body['gain_account_id'],{'REVENUE'});loss=account(company,body['loss_account_id'],{'EXPENSE'})
    from .ledger_engine import LedgerEngine
    lines=[{'account':account(company,r['account_id'],{'ASSET','LIABILITY','REVENUE','EXPENSE'}),'debit':r['debit'],'credit':r['credit']} for r in body['calculation']['lines']]
    journal=LedgerEngine.post_lines(tenant_id=company.pk,entry_date=date.fromisoformat(body['source']['as_of']),description='Reviewed monetary FX revaluation',lines_data=lines,actor=user,idempotency_key=event_id,period_id=body['period_id'])
    OutboxEvent.objects.create(id=uuid5(NS,'posted:'+review_id),event_type=POSTED,domain='accounting',aggregate_root=body['request_id'],version=1,payload={'company_id':str(company.pk),'review_id':review_id,'review_digest':fingerprint(body),'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    return outcome(company,user,row,journal,False)

@transaction.atomic
def state(company_id,*,actor,review_id):
    company=lock_company(company_id);user=current_actor(actor);row=OutboxEvent.objects.filter(pk=UUID(rates.uid(review_id))).first();body=read_review(company,row)
    if body['reviewed_by']!=str(user.pk):raise AccountingError('Own FX revaluation review required.')
    journal=JournalEntry.plain_objects.filter(tenant=company,financial_event_id=PREFIX+review_id,is_posted=True).first()
    if journal is None and (OutboxEvent.objects.filter(pk=uuid5(NS,'posted:'+review_id)).exists() or AccountingEventReceipt.objects.filter(tenant=company,event_id=PREFIX+review_id).exists()):raise AccountingError('FX journal evidence missing.')
    try:current=source(company,body['source']['account_id'],body['source']['currency'],body['source']['as_of'],exclude_journal=journal.pk if journal else None)==body['source']
    except (AccountingError,ValueError,TypeError):current=False
    return {'company_id':str(company.pk),'review_id':review_id,'preview':body,'source_current':current,'applied':outcome(company,user,row,journal,True) if journal else None,'read_only':True,'confirmations_restored':False,'ledger_written':False,'money_transferred':False,'rate_independently_verified':False}


@transaction.atomic
def catalog(company_id,*,actor):
    company=lock_company(company_id);current_actor(actor);result={};truncated=False
    for name,kinds in [('monetary',{'ASSET','LIABILITY'}),('gains',{'REVENUE'}),('losses',{'EXPENSE'})]:
        rows=list(Account.plain_objects.filter(tenant=company,chart_of_accounts__tenant=company,is_active=True,type__in=kinds).order_by('code','pk')[:101]);truncated=truncated or len(rows)>100
        result[name]=[{'id':str(r.pk),'code':r.code,'name':r.name,'type':r.type} for r in rows[:100]]
    return {'company_id':str(company.pk),'accounts':result,'truncated':truncated,'read_only':True,'ledger_written':False,'money_transferred':False,'rate_independently_verified':False}
