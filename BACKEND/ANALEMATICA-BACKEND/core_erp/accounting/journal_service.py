import logging
from datetime import date
from typing import List, Dict, Any
from django.db import transaction
from .models import JournalEntry, LedgerEntry, Account, FiscalPeriod

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
        # 1. Resolve Fiscal Period
        # Using plain_objects to bypass automatic filtering as we have the explicit tenant_id
        period = FiscalPeriod.plain_objects.filter(
            tenant_id=tenant_id,
            period_start__lte=entry_date,
            period_end__gte=entry_date,
            status='open'
        ).first()

        if not period:
            logger.error(f"No open fiscal period found for {entry_date} (Tenant: {tenant_id})")
            raise ValueError(f"No open fiscal period found for date {entry_date}")

        # 2. Create the Header
        entry = JournalEntry.objects.create(
            tenant_id=tenant_id,
            date=entry_date,
            description=description,
            reference=reference,
            period=period
        )

        # 3. Create Lines
        for line in lines_data:
            account = line['account']
            if isinstance(account, str):
                # Resolve by code if string
                account = Account.plain_objects.get(
                    tenant_id=tenant_id,
                    code=account
                )

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
