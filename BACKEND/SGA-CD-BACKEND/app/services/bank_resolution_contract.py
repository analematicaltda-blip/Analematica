"""Partial bank evidence must not be presented as a fully reconciled statement."""
import re

def money(value):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9]{1,26}\.[0-9]{2}',value):raise ValueError('Exact money required.')
    return int(value.replace('.',''))

def coverage(value):
    if not isinstance(value,dict) or set(value)!={'total_rows','matched_rows','unresolved_rows','matched_in','matched_out','unresolved_in','unresolved_out'}:raise ValueError('Explicit bounded coverage required.')
    if any(type(value[k]) is not int or not 0<=value[k]<=30 for k in ['total_rows','matched_rows','unresolved_rows']) or value['matched_rows']<1 or value['total_rows']!=value['matched_rows']+value['unresolved_rows']:raise ValueError('Invalid coverage counts.')
    for name in ('matched','unresolved'):
        for direction in ('in','out'):money(value[name+'_'+direction])

def result(data):
    c=data.get('coverage');coverage(c)
    if any(type(data.get(k)) is not bool for k in ['fully_reconciled','associations_confirmed','reconciliation_confirmed','released','requires_review']) or data.get('matched_rows')!=c['matched_rows']:raise ValueError('Explicit association qualification required.')
    full=data['associations_confirmed'] and not c['unresolved_rows']
    if data['fully_reconciled'] is not full or data['reconciliation_confirmed'] is not full or data['associations_confirmed'] and (data['released'] or data['requires_review']):raise ValueError('Partial or revoked associations cannot claim completeness.')
    assessment=data.get('period_assessment')
    if assessment is None:
        if data.get('period_source_current') is not None or data.get('period_reconciled') is not False or data.get('period_requires_review') is not False:raise ValueError('Period must be explicitly requested.')
    else:
        period(assessment,assessment['terms'])
        if type(data.get('period_source_current')) is not bool or data.get('period_reconciled') is not (full and data['period_source_current'] and assessment['eligible_for_period_reconciliation']) or data.get('period_requires_review') is not (not data['released'] and not data['period_source_current']):raise ValueError('Stale or incomplete period cannot claim reconciliation.')


def signed(value):
    if not isinstance(value,str) or not re.fullmatch(r'-?(0|[1-9][0-9]{0,25})[.][0-9]{2}',value) or value=='-0.00':raise ValueError('Canonical signed balance required.')
    return (-1 if value.startswith('-') else 1)*int(value.lstrip('-').replace('.',''))

def period(data,terms):
    from uuid import UUID
    from datetime import date
    if not isinstance(terms,dict) or set(terms)!={'since','until','opening','closing','statement_complete','evidence_digest'} or terms['statement_complete'] is not True or not re.fullmatch('[0-9a-f]{64}',terms['evidence_digest']):raise ValueError('Complete declared bank period required.')
    start,end=date.fromisoformat(terms['since']),date.fromisoformat(terms['until'])
    if start.isoformat()!=terms['since'] or end.isoformat()!=terms['until'] or start>end or (end-start).days>366:raise ValueError('Canonical bounded period required.')
    if not isinstance(data,dict) or data.get('schema')!='sgacd-bank-period-assessment-v1' or data.get('terms')!=terms or data.get('currency')!='COP' or data.get('scope')!='DECLARED_STATEMENT_AND_POSTED_CASH_ACCOUNT' or data.get('source_independently_verified') is not False:raise ValueError('Period scope mismatch.')
    for key in ('ledger_digest','policy_digest'):
        if not isinstance(data.get(key),str) or not re.fullmatch('[0-9a-f]{64}',data[key]):raise ValueError('Period proof missing.')
    opening,closing=signed(terms['opening']),signed(terms['closing']);bank_in,bank_out=money(data['bank_in']),money(data['bank_out']);book_open,book_close=signed(data['ledger_opening']),signed(data['ledger_closing']);book_in,book_out=money(data['ledger_in']),money(data['ledger_out'])
    if opening+bank_in-bank_out!=closing or book_open+book_in-book_out!=book_close or signed(data['opening_difference'])!=opening-book_open or signed(data['closing_difference'])!=closing-book_close or signed(data['flow_difference'])!=(bank_in-bank_out)-(book_in-book_out):raise ValueError('Period balances do not reconcile.')
    ids=data['unmatched_ledger_line_ids']
    if not isinstance(ids,list) or len(ids)>200 or len(set(ids))!=len(ids):raise ValueError('Bounded unique unmatched lines required.')
    for value in ids:
        if not isinstance(value,str) or str(UUID(value))!=value:raise ValueError('Invalid unmatched cash line.')
    for key,limit in [('ledger_history_rows',20000),('ledger_period_rows',200),('unresolved_bank_rows',30)]:
        if type(data.get(key)) is not int or not 0<=data[key]<=limit:raise ValueError('Invalid period coverage.')
    if data['ledger_period_rows']>data['ledger_history_rows'] or len(ids)>data['ledger_period_rows']:raise ValueError('Period coverage exceeds verified history.')
    equal=opening==book_open and closing==book_close
    if data.get('balances_match') is not equal or data.get('eligible_for_period_reconciliation') is not (equal and not ids and not data['unresolved_bank_rows']):raise ValueError('False period qualification.')

def preview(data,decisions):
    c=data.get('coverage');coverage(c);rows=data['rows'];differences=data['differences']
    if len(rows)!=c['matched_rows'] or len(differences)!=c['unresolved_rows']:raise ValueError('Coverage/source mismatch.')
    actual=[{'row':r['row'],'ledger_line_id':r['ledger_line_id'],'reason_code':None} for r in rows]+[{'row':r['row'],'ledger_line_id':None,'reason_code':r['reason_code']} for r in differences]
    if sorted(actual,key=lambda r:r['row'])!=sorted(decisions,key=lambda r:r['row']):raise ValueError('Statement resolutions changed.')
    for name,items in [('matched',rows),('unresolved',differences)]:
        for direction in ('IN','OUT'):
            if sum(money(r['amount']) for r in items if r['direction']==direction)!=money(c[name+'_'+direction.lower()]):raise ValueError('Source totals do not match coverage.')
