import logging
from .bank_transaction_model import BankTransaction
from apps.commercial_engine.models import SaaSInvoice
from apps.core_erp.audit_engine import AuditEngine

logger = logging.getLogger(__name__)

class TreasuryAudit:
    """
    Trazabilidad de Tesorería: Reconstruye la cadena Banco -> Pago -> Asiento.
    """

    @staticmethod
    def trace_reconciliation(transaction_id):
        """
        Devuelve el rastro completo de una transacción conciliada.
        """
        try:
            tx = BankTransaction.objects.get(id=transaction_id)

            trace = {
                'bank_transaction': {
                    'id': str(tx.id),
                    'external_id': tx.external_id,
                    'status': tx.reconciliation_status,
                    'hash': tx.audit_hash
                }
            }

            if tx.matched_invoice_id:
                invoice = SaaSInvoice.objects.get(id=tx.matched_invoice_id)
                trace['matched_invoice'] = {
                    'number': invoice.number,
                    'total': float(invoice.total_amount),
                    'status': invoice.status
                }

                # Aquí se buscarían los asientos contables relacionados en core_erp
                # trace['accounting_entry'] = ...

            return trace

        except Exception as e:
            logger.error(f"Error en TreasuryAudit: {str(e)}")
            return {'error': str(e)}
