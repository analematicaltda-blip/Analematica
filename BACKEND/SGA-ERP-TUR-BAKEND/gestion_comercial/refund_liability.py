"""Verified existing net-refund liability; no creation of fees or tax assumptions."""
from decimal import Decimal
from types import SimpleNamespace
from uuid import UUID
from django.utils import timezone
from apps.core_erp.outbox_models import OutboxEvent
from apps.core_erp.accounting.models import JournalEntry,LedgerEntry
from apps.core_erp.accounting.exceptions import AccountingError
from . import cancellation_policies as policy
USED_SOURCE='commercial.wallet-refund.source-used.v1'
def journal(company,j):
    if j is None or j.tenant_id!=company.pk or not j.is_posted or j.is_reversal or j.hash_version!='v2' or j.currency!='COP' or j.base_currency!='COP' or j.exchange_rate!=1 or not j.posted_at or j.compute_hash()!=j.system_hash or JournalEntry.plain_objects.filter(tenant=company,is_posted=True,reversed_entry_id=j.pk).exists():raise AccountingError('Posted source requires integrity/reversal reconciliation.')

def source_line(company,line_id,amount,day,*,available):
    row=LedgerEntry.plain_objects.select_for_update().select_related('account','account__chart_of_accounts','journal_entry').filter(pk=UUID(str(line_id)),tenant=company,account__tenant=company,account__chart_of_accounts__tenant=company,account__type='LIABILITY',account__is_active=True,journal_entry__tenant=company).first()
    if row is None:raise AccountingError('Existing active company refund liability required.')
    journal(company,row.journal_entry)
    if row.credit_amount!=Decimal(amount) or row.debit_amount!=0 or row.currency!='COP' or row.amount_transaction!=row.credit_amount or row.amount_base!=row.credit_amount or row.journal_entry.date>day:raise AccountingError('Refund liability credit must equal the net refund and precede settlement.')
    if available:
        proofs=list(OutboxEvent.objects.filter(event_type='commercial.wallet-refund.posted.v1',payload__company_id=str(company.pk))[:501])
        if len(proofs)>500:raise AccountingError('Se requiere archivo revisado del historial de devoluciones.')
        from . import wallet_refund
        for proof in proofs:
            bound=wallet_refund.binding(company,SimpleNamespace(pk=UUID(proof.payload['provider_id'])),proof.payload['body']['reservation_id'])
            if bound['liability_line_id']==str(row.pk):raise AccountingError('La obligación ya financió una devolución; una reserva ausente no libera capacidad.')
        if OutboxEvent.objects.filter(pk=policy.key(USED_SOURCE,company,str(row.pk))).exists():raise AccountingError('Refund liability credit already assigned to a settlement.')
        lines=LedgerEntry.plain_objects.filter(tenant=company,account=row.account,journal_entry__tenant=company,journal_entry__is_posted=True).select_related('journal_entry','account')
        rows=list(lines.order_by('pk')[:2001])
        if len(rows)>2000:raise AccountingError('Liability history requires a bounded reconciliation before settlement.')
        checked=set();balance=Decimal('0.00')
        for line in rows:
            j=line.journal_entry
            if j.pk not in checked:
                # Reversals can contribute to balance, but must themselves be valid.
                if j.hash_version!='v2' or j.currency!='COP' or j.base_currency!='COP' or j.exchange_rate!=1 or j.compute_hash()!=j.system_hash:raise AccountingError('Liability balance integrity requires reconciliation.')
                checked.add(j.pk)
            if line.currency!='COP' or line.amount_base!=line.debit_amount+line.credit_amount or line.amount_transaction!=line.amount_base:raise AccountingError('Liability valuation requires reconciliation.')
            balance+=line.credit_amount-line.debit_amount
        if balance<Decimal(amount):raise AccountingError('Remaining posted refund liability is insufficient.')
    return row

