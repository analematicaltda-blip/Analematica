import logging
from django.db import transaction

logger = logging.getLogger(__name__)

class PaymentStatusEngine:
    """
    Actualiza el estado de cobro en el ERP tras la conciliación.
    """

    @staticmethod
    @transaction.atomic
    def mark_as_paid(invoice, bank_tx):
        from apps.domain_business.comercial.models import ReciboCaja

        # 1. Crear Recibo de Caja (Adapter a admin_comercial)
        ReciboCaja.objects.create(
            perfil_ref_id=invoice.perfil_ref_id,
            factura=invoice,
            fecha_pago=bank_tx.date,
            monto=bank_tx.amount
        )

        # 2. Actualizar Factura
        invoice.status = 'PAID'
        invoice.save()

        # 3. Vincular transacción bancaria
        bank_tx.is_matched = True
        bank_tx.matched_invoice_id = invoice.id
        bank_tx.save()

        logger.info(f"Factura {invoice.number} marcada como PAGADA vía conciliación.")
        return True
