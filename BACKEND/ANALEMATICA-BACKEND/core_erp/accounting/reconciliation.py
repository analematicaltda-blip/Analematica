"""Bounded read-only reconciliation findings; no repairs, rehashing or market rates."""
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
from uuid import UUID
from django.db import transaction
from .models import Account,JournalEntry,LedgerEntry
from .ledger_engine import LedgerEngine
from .integrity import journal_hash
from .validation import lock_company,money
from .exceptions import AccountingError

@transaction.atomic
def inspect_company(tenant_id,*,after_id=None,limit=20):
    if type(limit) is not int or not 1<=limit<=50:raise AccountingError('Diagnostic limit must be from 1 to 50.')
    if after_id is not None:
        try:after_id=UUID(str(after_id))
        except (ValueError,TypeError,AttributeError):raise AccountingError('Invalid journal cursor.') from None
    company=lock_company(tenant_id)
    accounts=Account.plain_objects.filter(tenant_id=company.pk).exclude(initial_balance=0)
    posted=JournalEntry.plain_objects.filter(tenant_id=company.pk,is_posted=True)
    query=posted.order_by('pk')
    if after_id is not None:query=query.filter(pk__gt=after_id)
    found=list(query[:limit+1]);entries=[]
    for entry in found[:limit]:
        issues=set()
        lines=list(LedgerEntry.plain_objects.filter(journal_entry_id=entry.pk).select_related('account__chart_of_accounts').order_by('pk')[:1001])
        if len(lines)>1000:issues.add('LINE_LIMIT_REQUIRES_SEPARATE_REVIEW')
        else:
            try:LedgerEngine.validate_balance(entry,lines)
            except AccountingError:issues.add('TRANSACTION_BALANCE_OR_LINE_SCOPE_INVALID')
            if any(line.account.chart_of_accounts.tenant_id!=company.pk for line in lines):issues.add('ACCOUNT_CHART_SCOPE_INVALID')
            if entry.hash_version=='v2':
                try:
                    if entry.system_hash!=journal_hash(entry,lines,entry.previous_hash):issues.add('HASH_MISMATCH')
                except (AccountingError,ValueError,TypeError,InvalidOperation):issues.add('HASH_VALIDATION_UNAVAILABLE')
            elif entry.hash_version=='legacy':issues.add('LEGACY_HASH_REVIEW_REQUIRED')
            else:issues.add('UNKNOWN_HASH_VERSION_REVIEW_REQUIRED')
            for line in lines:
                try:
                    amount=money(line.debit_amount or line.credit_amount)
                    if line.currency!=entry.currency:issues.add('LINE_CURRENCY_MISMATCH')
                    if line.amount_transaction!=amount:issues.add('TRANSACTION_VALUATION_REVIEW_REQUIRED')
                    if entry.currency!=entry.base_currency:
                        if not entry.exchange_rate.is_finite() or entry.exchange_rate<=0:raise AccountingError('Invalid recorded rate.')
                        expected=money((amount*entry.exchange_rate).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))
                    else:
                        expected=amount
                        if entry.exchange_rate!=Decimal('1'):issues.add('SAME_CURRENCY_RATE_REVIEW_REQUIRED')
                    if line.amount_base!=expected:issues.add('BASE_VALUATION_REVIEW_REQUIRED')
                except (AccountingError,InvalidOperation,ValueError,TypeError):issues.add('VALUATION_INVALID')
        if not entry.posted_at:issues.add('POSTED_TIMESTAMP_MISSING')
        if entry.base_currency!=company.currency:issues.add('COMPANY_BASE_CURRENCY_REVIEW_REQUIRED')
        entries.append({'journal_id':str(entry.pk),'economic_date':entry.date.isoformat(),'hash_version':entry.hash_version,'findings':sorted(issues)})
    from .opening_balances import inspect_opening
    try:
        resolution=inspect_opening(company.pk)
        opening={'status':'RECONCILED_PRESERVED_REFERENCE',**resolution} if resolution else {'status':'NO_LEGACY_BALANCES'}
    except AccountingError:
        opening={'status':'REQUIRES_REVIEW'}
    return {'tenant_id':str(company.pk),'read_only':True,'repairs_executed':False,
        'posted_journal_count':posted.count(),'legacy_journal_count':posted.exclude(hash_version='v2').count(),
        'initial_balance_account_count':accounts.count(),'opening_reconciliation':opening,
        'initial_balance_accounts':[{'account_id':str(row.pk),'code':row.code} for row in accounts.order_by('pk')[:limit]],
        'initial_balance_sample_truncated':accounts.count()>limit,
        'entries':entries,'next_after':str(found[limit-1].pk) if len(found)>limit else None,
        'chain_validation_included':False,'full_ledger_certified':False,'snapshot_stable_across_pages':False,
        'scope':'Posted headers and bounded lines in this response; legacy findings require accountant review.'}
