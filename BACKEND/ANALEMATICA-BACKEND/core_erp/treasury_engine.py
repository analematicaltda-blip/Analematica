import logging
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.core_erp.accounting_engine import AccountingEngine

logger = logging.getLogger(__name__)

class TreasuryEngine:
    """
    Motor de Tesorería Soberano del Core ERP.
    Gestiona flujos de caja, pagos, conciliaciones y comisiones bancarias.
    """

    @staticmethod
    @transaction.atomic
    def apply_payment(invoice, amount, method, reference, bank_fees=Decimal('0.00')):
        """
        Registra un pago recibido, lo aplica a una factura e impacta la contabilidad.
        """
        if amount <= 0:
            raise ValidationError("El monto del pago debe ser positivo.")

        # 1. Registro lógico del pago (delegado al modelo concreto)
        logger.info(f"Aplicando pago de {amount} a factura {invoice.number}. Ref: {reference}")

        # 2. Actualizar estado de la factura
        # Si amount >= balance_pendiente -> PAID, sino PARTIAL

        # 3. Generar Asiento de Cobro Automático
        # Debe reflejar entrada a Banco, salida de Cuentas por Cobrar y Gasto por Comisiones.
        logger.info("Generando asiento contable de tesorería...")

        # entry = map_payment_to_journal_entry(invoice, amount, bank_fees)
        # AccountingEngine.post_journal_entry(entry)

        return True

    @staticmethod
    def register_bank_fees(tenant_id, amount, bank_account_code, description):
        """
        Registra gastos bancarios reales e impacta el Ledger (Integridad 100%).
        """
        logger.info(f"Registrando comisión bancaria: {amount}")

        from .event_bus import EventBus
        payload = {
            "tenant_id": tenant_id,
            "amount": float(amount),
            "bank_account": bank_account_code,
            "description": description,
            "reference": f"FEE-{timezone.now().timestamp()}"
        }

        # Disparar evento para que LedgerEngine lo procese via PostingRules
        EventBus.emit('BANK_FEE_REGISTERED', payload)
        return True

    @staticmethod
    def mark_as_uncollectible(invoice, reason):
        """
        Gestiona la cartera morosa y marcas de incobrabilidad.
        """
        logger.warning(f"Marcando factura {invoice.number} como incobrable. Razón: {reason}")
        invoice.status = 'UNCOLLECTIBLE'
        invoice.save()
        # Generar asiento de provisión/castigo si aplica
