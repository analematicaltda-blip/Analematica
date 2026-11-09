"""Owner-scoped statement comparison with actual posted cash lines; preview only.
Strict neutral CSV adapter, not an authenticated bank feed or a settlement engine.
Raw statement/transaction IDs are never persisted or included in the response.
"""
import csv,hashlib,io,re
from datetime import date
from uuid import UUID
from django.db import transaction
from django.utils import timezone
from .validation import lock_company
from .models import Account,JournalEntry,LedgerEntry
from .exceptions import AccountingError
from .invoice_intent import _money,_format_money
from . import ratios
from .reports_engine import ReportsEngine

COLUMNS=['transaction_id','date','direction','amount','currency']

def parse_statement(text):
    if not isinstance(text,str) or not 1<=len(text.encode('utf-8'))<=5000:raise AccountingError('CSV must contain at most 5000 UTF-8 bytes.')
    try:
        reader=csv.reader(io.StringIO(text),strict=True)
        if next(reader,None)!=COLUMNS:raise AccountingError('Use the exact neutral CSV header.')
        rows=[];seen=set()
        for cells in reader:
            if len(cells)!=5 or len(rows)>=100:raise AccountingError('At most 100 complete CSV rows required.')
            identifier,day,direction,amount,currency=cells
            if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._:-]{0,79}',identifier) or identifier in seen:raise AccountingError('Invalid or duplicated statement transaction reference.')
            parsed=date.fromisoformat(day)
            if parsed.isoformat()!=day or parsed>timezone.localdate():raise AccountingError('Canonical nonfuture statement date required.')
            cents=_money(amount)
            if cents<=0 or direction not in ('IN','OUT') or currency!='COP':raise AccountingError('Positive exact COP amount and IN/OUT direction required.')
            seen.add(identifier);rows.append({'id':identifier,'date':parsed,'direction':direction,'amount':cents})
    except (csv.Error,ValueError) as exc:raise AccountingError('Invalid neutral bank statement CSV.') from None
    if not rows or (max(r['date'] for r in rows)-min(r['date'] for r in rows)).days>366:raise AccountingError('Use one to 100 rows within an interval of at most 366 days.')
    return rows

def cash_account(company,account_id):
    identifier=UUID(str(account_id))
    policy=ratios.describe(ratios.latest(company.pk))
    if policy is None:raise AccountingError('A reviewed cash-account classification is required.')
    mapping=ratios.normalize(company.pk,policy['mapping'])
    if str(identifier) not in mapping['cash_equivalents']:raise AccountingError('Select an account explicitly reviewed as cash/equivalent.')
    account=Account.plain_objects.get(pk=identifier,tenant=company,is_active=True,chart_of_accounts__tenant=company,type='ASSET')
    return account,policy

@transaction.atomic
def compare_statement(company_id,*,account_id,csv_text):
    company=lock_company(company_id)
    if company.currency!='COP':raise AccountingError('No implicit FX is applied to bank statement comparisons.')
    account,policy=cash_account(company,account_id)
    rows=parse_statement(csv_text);start=min(r['date'] for r in rows);end=max(r['date'] for r in rows)
    snapshot=ReportsEngine.get_trial_balance(company.pk,end)['snapshot']
    candidates=LedgerEntry.plain_objects.filter(tenant=company,account=account,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__date__gte=start,journal_entry__date__lte=end)
    if candidates.exclude(currency='COP',journal_entry__currency='COP',journal_entry__base_currency='COP').exists():raise AccountingError('Foreign cash-account movements require a reviewed currency policy.')
    lines=list(candidates.filter(journal_entry__is_reversal=False).select_related('journal_entry').order_by('pk')[:2001])
    if len(lines)>2000:raise AccountingError('Narrow the comparison; more than 2000 ledger candidates.')
    reversed_ids=set(JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id__in=[r.journal_entry_id for r in lines]).values_list('reversed_entry_id',flat=True))
    index={};checked=set()
    for line in lines:
        journal=line.journal_entry
        if journal.pk in reversed_ids:continue
        if journal.pk not in checked:
            if journal.hash_version!='v2' or journal.compute_hash()!=journal.system_hash:raise AccountingError('Candidate journal requires integrity reconciliation.')
            checked.add(journal.pk)
        direction='IN' if line.debit_amount>0 else 'OUT';amount=_money(format(line.debit_amount or line.credit_amount,'.2f'))
        index.setdefault((journal.date,direction,amount),[]).append({'ledger_line_id':str(line.pk),'journal_id':str(journal.pk),'journal_hash':journal.system_hash})
    result=[]
    for number,row in enumerate(rows,1):
        matches=index.get((row['date'],row['direction'],row['amount']),[])
        ref=hashlib.sha256((str(company.pk)+':'+str(account.pk)+':'+row['id']).encode()).hexdigest()
        result.append({'row':number,'transaction_ref_digest':ref,'date':row['date'].isoformat(),'direction':row['direction'],'amount':_format_money(row['amount']),'status':'UNIQUE_CANDIDATE' if len(matches)==1 else 'AMBIGUOUS' if matches else 'UNMATCHED','candidate_count':len(matches),'candidates':matches[:10]})
    # Two imported transactions pointing at the same ledger line are ambiguous,
    # even when each individual amount/date lookup has only one candidate.
    usages={}
    for row in result:
        if row['status']=='UNIQUE_CANDIDATE':
            line=row['candidates'][0]['ledger_line_id'];usages[line]=usages.get(line,0)+1
    for row in result:
        if row['status']=='UNIQUE_CANDIDATE' and usages[row['candidates'][0]['ledger_line_id']]>1:row['status']='AMBIGUOUS_REUSED_LEDGER_LINE'
    return {'schema':'sgacd-bank-comparison-v1','company_id':str(company.pk),'account_id':str(account.pk),'currency':'COP','read_only':True,'source_digest':hashlib.sha256(csv_text.encode()).hexdigest(),'policy_revision':policy['revision'],'snapshot':snapshot,'rows':result,'summary':{status:sum(row['status']==status for row in result) for status in ('UNIQUE_CANDIDATE','AMBIGUOUS','UNMATCHED','AMBIGUOUS_REUSED_LEDGER_LINE')},'bank_connected':False,'bank_verified':False,'reconciliation_confirmed':False,'raw_statement_stored':False,'ledger_written':False,'money_transferred':False}
