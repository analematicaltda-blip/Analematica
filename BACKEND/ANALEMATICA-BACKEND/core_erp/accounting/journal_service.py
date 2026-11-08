import logging
from datetime import date
from typing import List, Dict, Any
from django.db import transaction
from .models import JournalEntry, LedgerEntry, Account, FiscalPeriod
from .validation import validate_lines
from .exceptions import AccountingError, TenantMismatchError, InactiveAccountError

logger = logging.getLogger(__name__)

class JournalService:
    """
    Service layer for Journal Entry lifecycle management.
    """
    @staticmethod
    @transaction.atomic
    def create_entry(
        tenant_id: str,
        entry_date: date,
        description: str,
        lines_data: List[Dict[str, Any]],
        reference: str = ""
    ) -> JournalEntry:
        """
        Creates a new journal entry with multiple lines.
        """
        normalized = validate_lines(lines_data)
        if not tenant_id:
            raise TenantMismatchError('An explicit accounting tenant is required.')
        # Resolve all accounts before creating a header; never trust a cached model.
        accounts = []
        for line in normalized:
            account = line.get('account')
            if isinstance(account, Account):
                if str(account.tenant_id) != str(tenant_id):
                    raise TenantMismatchError('Account belongs to another accounting company.')
                query = Account.plain_objects.filter(pk=account.pk, tenant_id=tenant_id)
            elif isinstance(account, str):
                query = Account.plain_objects.filter(code=account, tenant_id=tenant_id)
            else:
                raise AccountingError('Use a scoped account instance or an unambiguous account code.')
            found = list(query[:2])
            if len(found) != 1:
                raise AccountingError('Account is missing or ambiguous in this company.')
            accounts.append(found[0])
        locked = {a.pk: a for a in Account.plain_objects.select_for_update().filter(
            pk__in=[a.pk for a in accounts], tenant_id=tenant_id).order_by('pk')}
        for account in accounts:
            if account.pk not in locked or not locked[account.pk].is_active:
                raise InactiveAccountError('Account is unavailable or inactive.')
        # 1. Resolve Fiscal Period
        # Using plain_objects to bypass automatic filtering as we have the explicit tenant_id
        periods = list(FiscalPeriod.plain_objects.select_for_update().filter(
            tenant_id=tenant_id, period_start__lte=entry_date,
            period_end__gte=entry_date, status='open').order_by('pk')[:2])
        if len(periods) != 1:
            raise AccountingError('Exactly one open fiscal period must cover the entry date.')
        period = periods[0]

        # 2. Create the Header
        entry = JournalEntry.objects.create(
            tenant_id=tenant_id,
            date=entry_date,
            description=description,
            reference=reference,
            period=period
        )

        # 3. Create Lines
        for line, account in zip(normalized, accounts):
            account = locked[account.pk]

            LedgerEntry.objects.create(
                tenant_id=tenant_id,  # Mandatory for isolation
                journal_entry=entry,
                account=account,
                debit_amount=line.get('debit', line.get('debit_amount', 0)),
                credit_amount=line.get('credit', line.get('credit_amount', 0)),
                currency=line.get('currency', entry.currency),
                amount_transaction=line.get('amount_transaction', 0),
                description=line.get('description', description)
            )

        logger.info(f"Journal Entry created: {entry.id} ({description})")
        return entry
