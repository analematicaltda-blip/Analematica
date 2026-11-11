"""Exact declared fixed employee liabilities; no legal eligibility inference."""
import re
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.invoice_intent import _money,_format_money

def rules(values,components):
    if not isinstance(values,list) or not 1<=len(values)<=8:raise AccountingError('One to8 explicit fixed deduction rules required.')
    seen={c['code'] for c in components}
    for row in values:
        if not isinstance(row,dict) or set(row)!={'code','kind'} or not isinstance(row['code'],str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,29}',row['code']) or row['code'] in seen or row['kind']!='FIXED_EMPLOYEE_LIABILITY':raise AccountingError('Unique declared fixed liability deduction code required.')
        seen.add(row['code'])
    return sorted(values,key=lambda r:r['code'])

def calculate(values,policy,digest):
    if not isinstance(values,list) or len(values)>8:raise AccountingError('At most8 explicit fixed deductions per employee.')
    known={r['code'] for r in policy};seen=set();rows=[];total=0
    for row in values:
        if not isinstance(row,dict) or set(row)!={'code','amount','evidence_digest','authorization_digest'} or row['code'] not in known or row['code'] in seen:raise AccountingError('Unique known deduction with support and authorization references required.')
        digest(row['evidence_digest']);digest(row['authorization_digest']);amount=_money(row['amount'])
        if amount<=0:raise AccountingError('Positive exact deduction amount required; omit zero deductions.')
        seen.add(row['code']);total+=amount;rows.append({**row,'kind':'FIXED_EMPLOYEE_LIABILITY','amount':_format_money(amount),'authorization_independently_verified':False})
    return sorted(rows,key=lambda r:r['code']),total
