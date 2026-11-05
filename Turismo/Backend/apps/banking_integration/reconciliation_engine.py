from decimal import Decimal
from django.utils import timezone
from .models import BankTransaction
from apps.core_erp.accounting.models import LedgerEntry

class ReconciliationEngine:
    """
    Hallazgo 17: Motor de Conciliación Automática.
    Compara transacciones bancarias con movimientos contables.
    """

    @staticmethod
    def run_reconciliation(tenant_id):
        pending_txs = BankTransaction.objects.filter(tenant_id=tenant_id, status='PENDING')
        reconciled_count = 0

        for tx in pending_txs:
            # Algoritmo de matching: Monto exacto y Fecha cercana (+/- 3 días)
            match = LedgerEntry.objects.filter(
                tenant_id=tenant_id,
                amount_base=abs(tx.amount),
                journal_entry__date__range=[
                    tx.date - timezone.timedelta(days=3),
                    tx.date + timezone.timedelta(days=3)
                ]
            ).first()

            if match:
                tx.status = 'MATCHED'
                tx.reconciled_with_id = match.journal_entry.id
                tx.save()
                reconciled_count += 1
            else:
                tx.status = 'UNMATCHED'
                tx.save()

        return reconciled_count
