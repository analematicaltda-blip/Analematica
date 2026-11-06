import logging
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.core_erp.accounting_engine import AccountingEngine

logger = logging.getLogger(__name__)

class BillingEngine:
    """
    Motor de Facturación Soberano del Core ERP.
    Gestiona el ciclo de vida de facturas e impacta automáticamente la contabilidad.
    """

    @staticmethod
    def calculate_totals(invoice):
        """
        Calcula subtotales e impuestos de la factura.
        """
        lines = invoice.lines.all()
        subtotal = sum(line.subtotal for line in lines)
        total_tax = sum(line.tax_amount for line in lines)

        invoice.total_amount = subtotal + total_tax
        invoice.tax_amount = total_tax
        invoice.save()
        return invoice.total_amount

    @staticmethod
    @transaction.atomic
    def issue_invoice(invoice, responsible_user=None):
        """
        Emite la factura y genera el impacto contable obligatorio.
        """
        if invoice.status != 'DRAFT':
            raise ValidationError(f"Solo se pueden emitir facturas en borrador. Estado actual: {invoice.status}")

        # 1. Asegurar cálculos finales
        BillingEngine.calculate_totals(invoice)

        # 2. Cambiar estado
        invoice.status = 'ISSUED'
        invoice.save()

        # 3. Generar Asiento Contable Automático (Accounting Impact)
        # Nota: La creación del objeto 'entry' y sus 'lines' depende de la implementación del modelo concreto.
        # Aquí definimos el flujo de orquestación.

        logger.info(f"Factura {invoice.number} emitida.")

        # El impacto contable se delega al orquestador que conoce los modelos concretos
        # o se dispara vía eventos. Emitimos el evento para que Accounting pueda reaccionar.
        from apps.core_erp.event_bus import EventBus
        EventBus.emit(EventBus.INVOICE_CREATED, {
            'invoice_id': str(invoice.id),
            'total_amount': float(invoice.total_amount),
            'company_id': str(getattr(invoice, 'company_id', ''))
        })

        return invoice

    @staticmethod
    def validate_invoice(invoice):
        """
        Validación básica de integridad de la factura.
        """
        if not invoice.number:
            raise ValidationError("La factura debe tener un número asignado.")
        if invoice.total_amount <= 0:
            raise ValidationError("El monto total de la factura debe ser mayor a cero.")
        return True

    @staticmethod
    def process_usage_billing(entity_id, usage_data):
        """
        Genera facturación basada en consumo (API calls, tokens, etc).
        """
        logger.info(f"Procesando facturación por uso para la entidad {entity_id}")
        # Hallazgo March 2026: Sincronización con el motor de facturación por uso
        try:
            from apps.usage_billing.usage_collector import UsageCollector
            from apps.usage_billing.usage_billing_engine import UsageBillingEngine

            # 1. Registrar eventos de consumo
            for metric_code, quantity in usage_data.items():
                UsageCollector.record_event(
                    metric_code=metric_code,
                    quantity=quantity,
                    company_id=entity_id,
                    metadata={"source": "BillingEngine.manual_trigger"}
                )

            # 2. El proceso automático de cierre de ciclo (UsageBillingEngine)
            # se encargará de generar la factura. Aquí retornamos éxito de registro.
            return {"status": "usage_recorded", "entity_id": entity_id}

        except ImportError:
            logger.error("Módulo usage_billing no disponible. Facturación por uso desactivada.")
            return {"status": "module_missing", "error": True}
