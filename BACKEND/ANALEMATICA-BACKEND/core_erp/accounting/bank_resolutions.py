"""Explicit statement-row decisions. Differences are evidence, never postings."""
from uuid import UUID
from .exceptions import AccountingError
from .invoice_intent import _money,_format_money
REASONS={'BANK_FEE_UNPOSTED','TIMING_DIFFERENCE','UNIDENTIFIED','REQUIRES_ADJUSTMENT'}

def coverage(rows,differences):
    result={'total_rows':len(rows)+len(differences),'matched_rows':len(rows),'unresolved_rows':len(differences)}
    for name,items in [('matched',rows),('unresolved',differences)]:
        for direction in ('IN','OUT'):result[name+'_'+direction.lower()]=_format_money(sum(_money(r['amount']) for r in items if r['direction']==direction))
    return result

def resolve(rows,decisions):
    if not isinstance(decisions,list) or len(decisions)!=len(rows):raise AccountingError('Choose one explicit resolution for every statement row.')
    seen=set();selected={};lines=set();matches=[];differences=[]
    for decision in decisions:
        if not isinstance(decision,dict) or set(decision)!={'row','ledger_line_id','reason_code'} or type(decision['row']) is not int or decision['row'] in seen:raise AccountingError('Unique exact row/line/reason resolution required.')
        seen.add(decision['row']);selected[decision['row']]=decision
    if seen!={r['row'] for r in rows}:raise AccountingError('Resolution rows differ from the imported statement.')
    for row in rows:
        decision=selected[row['row']];base={k:row[k] for k in ['row','transaction_ref_digest','date','direction','amount']}
        if decision['ledger_line_id'] is None:
            if decision['reason_code'] not in REASONS:raise AccountingError('Explicit supported difference reason required.')
            differences.append({**base,'reason_code':decision['reason_code']})
        else:
            identifier=decision['ledger_line_id']
            if not isinstance(identifier,str) or str(UUID(identifier))!=identifier or decision['reason_code'] is not None or identifier in lines:raise AccountingError('A ledger line can be selected only once, without a difference reason.')
            candidate=next((c for c in row['candidates'] if c['ledger_line_id']==identifier),None)
            if candidate is None:raise AccountingError('Select an actual same-date/amount/direction candidate in this company/account.')
            lines.add(identifier);matches.append(base|candidate)
    if not matches:raise AccountingError('At least one actual matched movement is required; an all-differences report is not a reconciliation.')
    return matches,differences
