import logging
from django.db.models import Sum, Max, Avg, Count
from django.db import transaction
from .usage_event_model import UsageEvent
from .usage_aggregation_model import UsageAggregation
from .usage_metric_model import UsageMetric
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class AggregationEngine:
    """
    Consolida eventos individuales en totales por suscripción y periodo.
    """

    @staticmethod
    @transaction.atomic
    def aggregate_for_subscription(subscription, metric, period_start, period_end):
        """
        Calcula el total de uso para una suscripción y métrica en un periodo.
        Soporta recalculo.
        """
        # 1. Filtrar eventos del periodo
        events = UsageEvent.objects.filter(
            subscription=subscription,
            metric=metric,
            timestamp__date__range=(period_start, period_end)
        )

        # 2. Aplicar tipo de agregación según la métrica
        if metric.aggregation_type == UsageMetric.AggregationType.SUM:
            agg_result = events.aggregate(result=Sum('quantity'))['result'] or 0
        elif metric.aggregation_type == UsageMetric.AggregationType.MAX:
            agg_result = events.aggregate(result=Max('quantity'))['result'] or 0
        elif metric.aggregation_type == UsageMetric.AggregationType.AVG:
            agg_result = events.aggregate(result=Avg('quantity'))['result'] or 0
        elif metric.aggregation_type == UsageMetric.AggregationType.COUNT:
            agg_result = events.count()
        else:
            agg_result = 0

        # 3. Guardar en UsageAggregation
        aggregation, _ = UsageAggregation.objects.update_or_create(
            subscription=subscription,
            metric=metric,
            period_start=period_start,
            period_end=period_end,
            defaults={'total_quantity': agg_result}
        )

        # 4. Emitir Evento
        EventBus.emit('USAGE_AGGREGATED', {
            'aggregation_id': str(aggregation.id),
            'subscription_id': str(subscription.id),
            'metric_code': metric.code,
            'total_quantity': float(agg_result)
        })

        return aggregation

    @staticmethod
    def process_all_active_metrics(subscription, period_start, period_end):
        """
        Consolida todas las métricas facturables para una suscripción.
        """
        metrics = UsageMetric.objects.filter(is_active=True, billable=True)
        results = []
        for metric in metrics:
            agg = AggregationEngine.aggregate_for_subscription(subscription, metric, period_start, period_end)
            results.append(agg)
        return results
