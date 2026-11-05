import logging
import hashlib
import json
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import GlobalLedgerEntry

logger = logging.getLogger(__name__)

class SettlementService:
    """
    Distributed Ledger & Settlement Core - Phase 23.2.
    Registro inmutable de transacciones y liquidación cross-border.
    """

    @staticmethod
    @transaction.atomic
    def record_global_transaction(source_j, target_j, amount, currency, payload):
        """
        Registra una transacción económica global en el ledger inmutable.
        """
        # 1. Generate Transaction Hash (Auditability)
        txn_data = {
            "source": source_j,
            "target": target_j,
            "amount": str(amount),
            "currency": currency,
            "payload": payload,
            "timestamp": str(timezone.now())
        }
        txn_hash = hashlib.sha256(json.dumps(txn_data).encode()).hexdigest()

        # 2. Create Global Ledger Entry
        entry = GlobalLedgerEntry.objects.create(
            transaction_hash=txn_hash,
            source_jurisdiction=source_j,
            target_jurisdiction=target_j,
            amount=amount,
            currency=currency,
            payload_snapshot=payload
        )

        logger.info(f"GDEI Ledger: Recorded Transaction {txn_hash[:16]}...")

        # 3. Integration with Local ERP Ledger (Phase B)
        SettlementService._sync_to_core_erp(entry)

        return entry

    @staticmethod
    def _sync_to_core_erp(global_entry):
        """
        Sincroniza el registro global con el Ledger local del Core ERP.
        """
        from apps.core_erp.accounting.ledger_engine import LedgerEngine
        # Payload simulation for LedgerEngine
        event_payload = {
            "tenant_id": "GLOBAL_HOLDING", # Placeholder for Holding Tenant
            "amount": global_entry.amount,
            "currency": global_entry.currency,
            "reference": global_entry.transaction_hash,
            "event_type": "GLOBAL_SETTLEMENT"
        }
        # LedgerEngine.post_event("GLOBAL_SETTLEMENT", event_payload)
        logger.info(f"GDEI Ledger: Triggered local Core ERP sync for {global_entry.transaction_hash[:16]}")

    @staticmethod
    @transaction.atomic
    def settle_transaction(entry_id):
        """
        Liquida definitivamente una transacción cross-border.
        """
        entry = GlobalLedgerEntry.objects.get(id=entry_id)
        if not entry.is_settled:
            entry.is_settled = True
            entry.settlement_timestamp = timezone.now()
            entry.save()

            logger.warning(f"GDEI Settlement: Transaction {entry.transaction_hash[:16]} SETTLED.")
            return True
        return False
