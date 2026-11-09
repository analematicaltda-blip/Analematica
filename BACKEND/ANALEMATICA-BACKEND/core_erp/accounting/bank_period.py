"""Owner-declared bank-period arithmetic and authoritative scoped ledger coverage.
No bank authentication, inferred opening balance, posting or adjustment.
"""
import re,hashlib
from datetime import date
from django.utils import timezone
from .exceptions import AccountingError
from .integrity import canonical
from .invoice_intent import _money
from .models import LedgerEntry
from .bank_statement import cash_account


def signed(value):
    if not isinstance(value,str) or not re.fullmatch(r'-?(0|[1-9][0-9]{0,15})\.[0-9]{2}',value) or value=='-0.00':raise AccountingError('Canonical exact signed balance required.')
    return (-1 if value.startswith('-') else 1)*int(value.lstrip('-').replace('.',''))

def fmt(value):return ('-' if value<0 else '')+str(abs(value)//100)+'.'+str(abs(value)%100).zfill(2)

def assess(company,account_id,terms,rows,differences):
    if not isinstance(terms,dict) or set(terms)!={'since','until','opening','closing','statement_complete','evidence_digest'} or terms['statement_complete'] is not True or not isinstance(terms['evidence_digest'],str) or not re.fullmatch('[0-9a-f]{64}',terms['evidence_digest']):raise AccountingError('Explicit complete-statement declaration, dates, balances and evidence required.')
    start,end=date.fromisoformat(terms['since']),date.fromisoformat(terms['until'])
    if start.isoformat()!=terms['since'] or end.isoformat()!=terms['until'] or start>end or end>timezone.localdate() or (end-start).days>366:raise AccountingError('Canonical closed nonfuture period of at most367 days required.')
    all_rows=rows+differences
    if not all_rows or any(not terms['since']<=r['date']<=terms['until'] for r in all_rows):raise AccountingError('Every imported bank row must belong to the declared period.')
    opening,closing=signed(terms['opening']),signed(terms['closing'])
    bank_in=sum(_money(r['amount']) for r in all_rows if r['direction']=='IN');bank_out=sum(_money(r['amount']) for r in all_rows if r['direction']=='OUT')
    if opening+bank_in-bank_out!=closing:raise AccountingError('Declared bank opening plus imported inflows minus outflows must equal declared closing.')
    account,policy=cash_account(company,account_id)
    from .opening_balances import inspect_opening
    inspect_opening(company.pk,cutoff=end)
    lines=list(LedgerEntry.plain_objects.filter(tenant=company,account=account,journal_entry__tenant=company,journal_entry__is_posted=True,journal_entry__date__lte=end).select_related('journal_entry').order_by('pk')[:2001])
    if len(lines)>2000:raise AccountingError('This bounded period assessment supports at most2000 historical cash lines; use a qualified historical snapshot for larger histories.')
    digest=hashlib.sha256();checked=set();book_opening=book_in=book_out=0;period_ids=[]
    for line in lines:
        journal=line.journal_entry
        if journal.hash_version!='v2' or journal.currency!='COP' or journal.base_currency!='COP' or journal.exchange_rate!=1 or line.currency!='COP' or line.amount_transaction!=line.debit_amount+line.credit_amount or line.amount_base!=line.debit_amount+line.credit_amount:raise AccountingError('Period assessment requires qualified COP ledger history.')
        if journal.pk not in checked:
            if journal.compute_hash()!=journal.system_hash:raise AccountingError('Cash journal integrity changed.')
            checked.add(journal.pk)
        debit,credit=_money(format(line.debit_amount,'.2f')),_money(format(line.credit_amount,'.2f'))
        digest.update((canonical({'line_id':str(line.pk),'journal_id':str(journal.pk),'journal_hash':journal.system_hash,'date':journal.date.isoformat(),'debit':debit,'credit':credit})+'\n').encode())
        if journal.date<start:book_opening+=debit-credit
        else:book_in+=debit;book_out+=credit;period_ids.append(str(line.pk))
    if len(period_ids)>200:raise AccountingError('Narrow the period; at most200 cash movements per assessment.')
    matched={r['ledger_line_id'] for r in rows};unmatched=sorted(set(period_ids)-matched)
    if matched-set(period_ids):raise AccountingError('Matched cash lines are outside the declared period.')
    book_closing=book_opening+book_in-book_out;opening_difference=opening-book_opening;closing_difference=closing-book_closing
    return {'schema':'sgacd-bank-period-assessment-v1','terms':terms,'currency':'COP','scope':'DECLARED_STATEMENT_AND_POSTED_CASH_ACCOUNT','ledger_digest':digest.hexdigest(),'policy_digest':policy['digest'],'bank_in':fmt(bank_in),'bank_out':fmt(bank_out),'ledger_opening':fmt(book_opening),'ledger_closing':fmt(book_closing),'ledger_in':fmt(book_in),'ledger_out':fmt(book_out),'opening_difference':fmt(opening_difference),'closing_difference':fmt(closing_difference),'flow_difference':fmt((bank_in-bank_out)-(book_in-book_out)),'unmatched_ledger_line_ids':unmatched,'ledger_history_rows':len(lines),'ledger_period_rows':len(period_ids),'unresolved_bank_rows':len(differences),'balances_match':opening_difference==closing_difference==0,'eligible_for_period_reconciliation':opening_difference==closing_difference==0 and not unmatched and not differences,'source_independently_verified':False}
