"""Exact capacity from verified active proofs, not mutable claim indexes alone.
Caller holds the company lock. Missing/tampered claims never free capacity.
"""
from .exceptions import AccountingError
from django.db.models import Q
from .invoice_intent import _money,_format_money
from apps.core_erp.outbox_models import OutboxEvent

def totals(groups,lines):
    ledger={r['ledger_line_id']:r for r in lines};values={}
    for group in groups:
        allocations=group.get('ledger_allocations')
        if allocations is None:allocations=[{'ledger_line_id':i,'amount':ledger[i]['amount']} for i in group['ledger_line_ids']]
        for row in allocations:values[row['ledger_line_id']]=values.get(row['ledger_line_id'],0)+_money(row['amount'])
    return {k:_format_money(v) for k,v in sorted(values.items())}

def balances(company,lines):
    from . import bank_reconciliation as legacy,bank_grouped as grouped,bank_groups as recovery
    ledger={r['ledger_line_id']:r for r in lines};used={key:0 for key in ledger}
    if not ledger:return []
    proofs=list(OutboxEvent.objects.filter(event_type__in=(legacy.APPLIED,legacy.APPLIED_V2,grouped.APPLIED,recovery.APPLIED)).filter(Q(payload__company_id=str(company.pk))|Q(payload__body__company_id=str(company.pk))).order_by('pk')[:1001])
    if len(proofs)>1000:raise AccountingError('Capacity history exceeds1000 company confirmations; reviewed archival is required.')
    identifiers=[str(p.pk) for p in proofs]
    if OutboxEvent.objects.filter(event_type=legacy.CLAIM,payload__company_id=str(company.pk)).exclude(payload__reconciliation_id__in=identifiers).exists():raise AccountingError('Orphan bank claim requires reconciliation; capacity is not silently released.')
    for proof in proofs:
        if proof.event_type==grouped.APPLIED:
            body=grouped.origin(company,proof);freed=grouped.released(company,proof);records=body['ledger_lines'];amounts=body.get('allocation_totals')
        elif proof.event_type==recovery.APPLIED:
            body=recovery.origin(company,proof);freed=legacy._released(company,proof);records=body['lines'];amounts=None
        else:body=legacy._origin(company,proof);freed=legacy._released(company,proof);records=body['rows'];amounts=None
        if not freed:
            for row in records:
                key=row['ledger_line_id']
                if key in used:
                    amount=_money(amounts[key] if amounts is not None else row['amount'])
                    if amount<=0:raise AccountingError('A capacity claim must be positive.')
                    used[key]+=amount
    result=[]
    for key,row in sorted(ledger.items()):
        gross=_money(row['amount'])
        if used[key]>gross:raise AccountingError('Claims exceed original cash amount; reconciliation required.')
        result.append({'ledger_line_id':key,'amount':row['amount'],'reserved_amount':_format_money(used[key]),'available_amount':_format_money(gross-used[key])})
    return result
