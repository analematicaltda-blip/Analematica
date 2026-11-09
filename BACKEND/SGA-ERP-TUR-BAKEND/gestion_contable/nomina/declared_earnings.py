"""Exact owner-declared supplements; no automatic legal/time classification."""
import re
from apps.core_erp.accounting.exceptions import AccountingError
from apps.core_erp.accounting.invoice_intent import _format_money

FIELDS={'OVERTIME':'horas_extras','SURCHARGE':'recargos'}
def rules(values):
    if not isinstance(values,list) or not 1<=len(values)<=8:raise AccountingError('One to8 explicit earning rules required.')
    seen=set()
    for row in values:
        if not isinstance(row,dict) or set(row)!={'code','kind','rate_bps','hour_divisor'} or not isinstance(row['code'],str) or not re.fullmatch('[A-Z0-9][A-Z0-9_-]{0,29}',row['code']) or row['code'] in seen or row['kind'] not in FIELDS or type(row['rate_bps']) is not int or not 1<=row['rate_bps']<=50000 or type(row['hour_divisor']) is not int or not 1<=row['hour_divisor']<=1000:raise AccountingError('Explicit unique earning identity, hourly divisor and integer rate required.')
        seen.add(row['code'])
    return sorted(values,key=lambda row:row['code'])

def calculate(values,policy,salary,period_days,digest):
    if not isinstance(values,list) or len(values)>8:raise AccountingError('Bounded declared earning minutes required.')
    terms={r['code']:r for r in policy};seen=set();result=[];totals={v:0 for v in FIELDS.values()};minutes=0
    for row in values:
        if not isinstance(row,dict) or set(row)!={'code','minutes','evidence_digest'} or row['code'] not in terms or row['code'] in seen or type(row['minutes']) is not int or not 1<=row['minutes']<=period_days*1440:raise AccountingError('Unique supported earning and positive bounded integer minutes required.')
        seen.add(row['code']);digest(row['evidence_digest']);rule=terms[row['code']];minutes+=row['minutes']
        numerator=salary*row['minutes']*rule['rate_bps'];denominator=rule['hour_divisor']*60*10000
        cents=(numerator*2+denominator)//(2*denominator)
        if cents<=0:raise AccountingError('Declared earning rounds to zero; reconcile source precision.')
        totals[FIELDS[rule['kind']]]+=cents;result.append({**row,**rule,'amount':_format_money(cents)})
    if minutes>period_days*1440:raise AccountingError('Declared supplemental minutes exceed physical period capacity.')
    return sorted(result,key=lambda row:row['code']),totals
