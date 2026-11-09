"""Versioned canonical journal hashes. Legacy rows are never rewritten."""
import hashlib
import json
from decimal import Decimal
from .exceptions import AccountingError


def canonical(value):
    def normalize(item):
        if isinstance(item, float):
            raise AccountingError('Binary floats are not accepted in financial event contracts.')
        if isinstance(item, Decimal):
            if not item.is_finite():raise AccountingError('Nonfinite decimal event value.')
            return format(item, 'f')
        if isinstance(item, dict):
            if not all(isinstance(key,str) for key in item):raise AccountingError('Event keys must be strings.')
            return {key:normalize(val) for key,val in item.items()}
        if isinstance(item,(list,tuple)):return [normalize(val) for val in item]
        if item is None or isinstance(item,(str,int,bool)):return item
        raise AccountingError('Unsupported event contract value.')
    return json.dumps(normalize(value),sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)


def fingerprint(value):
    text=canonical(value)
    if len(text.encode())>32768:raise AccountingError('Event contract is too large.')
    return hashlib.sha256(text.encode()).hexdigest()


def journal_hash(entry, lines, previous_hash):
    value={'schema':'sgacd-ledger-v2','id':str(entry.pk),'tenant_id':str(entry.tenant_id),
           'period_id':str(entry.period_id),'date':entry.date.isoformat(),'reference':entry.reference,
           'description':entry.description,'currency':entry.currency,'base_currency':entry.base_currency,
           'exchange_rate':format(Decimal(entry.exchange_rate),'.6f'),'actor_id':entry.created_by_id,
           'event_type':entry.event_type,'financial_event_id':entry.financial_event_id,
           'correlation_id':entry.correlation_id,'rule_version':entry.rule_version,
           'is_reversal':entry.is_reversal,'reversed_entry_id':str(entry.reversed_entry_id) if entry.reversed_entry_id else None,
           'posted_at':entry.posted_at.isoformat() if entry.posted_at else None,'previous_hash':previous_hash,
           'lines':[{'id':str(line.pk),'tenant_id':str(line.tenant_id),'account_id':str(line.account_id),
                     'chart_id':str(line.account.chart_of_accounts_id),'account_code':line.account.code,'account_type':line.account.type,
                     'debit':format(line.debit_amount,'.2f'),'credit':format(line.credit_amount,'.2f'),
                     'currency':line.currency,'amount_transaction':format(line.amount_transaction,'.2f'),
                     'amount_base':format(line.amount_base,'.2f'),'description':line.description}
                    for line in sorted(lines,key=lambda row:str(row.pk))]}
    return hashlib.sha256(canonical(value).encode()).hexdigest()
