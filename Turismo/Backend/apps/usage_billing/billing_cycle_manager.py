import logging
from datetime import date, timedelta
from django.utils import timezone
from .usage_aggregation_engine import AggregationEngine
from apps.commercial_engine.models import SaaSSubscription
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class BillingCycleManager:
    """
    Gestiona el ciclo de vida temporal de la facturación por uso.
    """

    @staticmethod
    def close_cycle_for_subscription(subscription):
        """
        Cierra el ciclo actual, agrega uso y dispara la facturación.
        """
        # Simplificación: el periodo es el mes anterior a hoy si hoy es día de corte
        # o el periodo definido por la suscripción.
        # Para esta implementación, usaremos los últimos 30 días.
        today = date.today()
        period_end = today
        period_start = today - timedelta(days=30)

        logger.info(f"Cerrando ciclo para {subscription.company_id}: {period_start} a {period_end}")

        # 1. Consolidar Uso
        aggregations = AggregationEngine.process_all_active_metrics(subscription, period_start, period_end)

        # 2. Emitir Evento de Cierre
        EventBus.emit('USAGE_CYCLE_CLOSED', {
            'subscription_id': str(subscription.id),
            'company_id': str(subscription.company_id),
            'period_start': str(period_start),
            'period_end': str(period_end),
            'aggregation_ids': [str(a.id) for a in aggregations]
        })

        return aggregations

    @staticmethod
    def run_daily_check():
        """
        Busca suscripciones cuyo renewal_date sea hoy para cerrar ciclo.
        """
        today = date.today()
        subscriptions = SaaSSubscription.objects.filter(renewal_date=today, is_active=True)
        for sub in subscriptions:
            BillingCycleManager.close_cycle_for_subscription(sub)
