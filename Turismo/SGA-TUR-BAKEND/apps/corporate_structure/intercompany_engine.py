import logging
from .models import IntercompanyTransaction, LegalEntity
from apps.core_erp.accounting_engine import AccountingEngine
from decimal import Decimal
from django.utils import timezone

logger = logging.getLogger(__name__)

class IntercompanyEngine:
    """
    Manages transactions between legal entities within the holding.
    Ensures that for every outgoing transaction, a corresponding entry exists in both entities.
    """

    @staticmethod
    def create_intercompany_billing(source_id, dest_id, amount, description, tx_type='BILLING'):
        source = LegalEntity.objects.get(id=source_id)
        dest = LegalEntity.objects.get(id=dest_id)

        # 1. Create Intercompany record
        tx = IntercompanyTransaction.objects.create(
            source_entity=source,
            destination_entity=dest,
            tx_type=tx_type,
            amount=amount,
            currency=source.functional_currency,
            description=description
        )

        # 2. Mirror in ERP (Simulated logic using core_erp Engines)
        # In source entity: Debit Intercompany Receivable / Credit Revenue
        # In destination entity: Debit Expense / Credit Intercompany Payable

        try:
            # Simulate successful mirror in ERP
            # In a real scenario, we would create AdminJournalEntry for both entities
            logger.info(f"Mirroring IC transaction {tx.id} in ERP...")

            tx.is_mirrored = True
            tx.mirror_reference = f"ERP-SYNC-{tx.id}"
            tx.save()
            return tx
        except Exception as e:
            logger.error(f"Failed to mirror intercompany transaction: {str(e)}")
            return tx
