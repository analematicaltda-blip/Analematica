import logging
from django.db import transaction
from django.utils import timezone
from .models import UsageAggregation
from .rating_engine import RatingEngine
from apps.commercial_engine.models import SaaSSubscription, SaaSInvoice, SaaSInvoiceLine
from apps.core_erp.billing_engine import BillingEngine
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class UsageBillingEngine:
    """
    Motor final que convierte agregaciones calificadas en cargos reales de factura.
    """

    @staticmethod
    @transaction.atomic
    def bill_aggregations(subscription_id, aggregation_ids):
        """
        Genera cargos de facturación para un conjunto de agregaciones.
        """
        subscription = SaaSSubscription.objects.get(id=subscription_id)
        aggregations = UsageAggregation.objects.filter(id__in=aggregation_ids, is_billed=False)

        if not aggregations.exists():
            logger.warning("No hay agregaciones pendientes de facturar.")
            return None

        # 1. Crear o Buscar Factura del Periodo (usualmente una factura de renovación)
        # Para simplificar, creamos una factura de "Uso de Recursos"
        invoice = SaaSInvoice.objects.create(
            subscription=subscription,
            company_id=subscription.company_id,
            number=f"INV-USAGE-{timezone.now().strftime('%Y%m%d')}-{subscription.id.hex[:4].upper()}",
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=5),
            total_amount=0
        )

        total_usage_amount = 0

        for agg in aggregations:
            # 2. Calcular Precio
            total_price = RatingEngine.calculate_price(agg.metric, agg.total_quantity)

            if total_price > 0:
                # 3. Generar Línea de Factura
                SaaSInvoiceLine.objects.create(
                    invoice=invoice,
                    description=f"Consumo {agg.metric.name} ({agg.total_quantity} {agg.metric.unit})",
                    quantity=agg.total_quantity,
                    unit_price=total_price / agg.total_quantity if agg.total_quantity > 0 else 0,
                    subtotal=total_price
                )
                total_usage_amount += total_price

            # 4. Marcar como facturado
            agg.is_billed = True
            agg.billed_at = timezone.now()
            agg.save()

        # 5. Finalizar Factura e Impacto Contable
        BillingEngine.issue_invoice(invoice)

        # Disparar impacto contable (usando el método que creamos en Phase 2)
        from apps.commercial_engine.subscription_engine import SubscriptionEngine
        SubscriptionEngine.create_accounting_impact(invoice)

        # 6. Emitir Evento
        EventBus.emit('USAGE_BILLED', {
            'invoice_id': str(invoice.id),
            'subscription_id': str(subscription_id),
            'amount': float(total_usage_amount)
        })

        return invoice

    @classmethod
    def handle_cycle_closed(cls, payload):
        """Subscriber para USAGE_CYCLE_CLOSED"""
        cls.bill_aggregations(payload['subscription_id'], payload['aggregation_ids'])
