from .models import SaaSMetric, RevenueForecast
from .metrics_engine import MetricsEngine
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ForecastEngine:
    """
    Projects revenue and cashflow based on historical trends.
    """

    @staticmethod
    def generate_forecasts():
        mrr = MetricsEngine.calculate_mrr()
        churn_rate = MetricsEngine.calculate_churn_rate() / 100 # as decimal

        # Calculate historical growth rate (last 3 months)
        # Simplified for MVP: assume 10% monthly growth if enough data exists
        growth_rate = Decimal('0.10')

        net_growth = growth_rate - churn_rate

        now = timezone.now().date()

        # Forecast for 12 months
        current_projected_mrr = mrr
        for i in range(1, 13):
            forecast_date = now + timezone.timedelta(days=i*30)
            current_projected_mrr = current_projected_mrr * (1 + net_growth)

            # Cashflow projection: MRR + Usage (assume usage is 20% of MRR)
            projected_revenue = current_projected_mrr * Decimal('1.20')

            RevenueForecast.objects.update_or_create(
                forecast_date=forecast_date,
                algorithm_version='Linear-Growth-V1',
                defaults={
                    'projected_revenue': projected_revenue,
                    'projected_cashflow': projected_revenue * Decimal('0.90'), # Assume 10% operational costs
                    'confidence_interval': Decimal('85.00')
                }
            )

        logger.info(f"Forecasts generated for 12 months based on MRR {mrr}")

        # EOS Activation: Decision Engine Integration
        from apps.core_erp.event_bus import EventBus
        EventBus.emit("STRATEGIC_SIGNAL_EMITTED", {
            "source": "ForecastEngine",
            "type": "REVENUE_TREND",
            "value": float(net_growth),
            "metadata": {"growth": float(growth_rate), "churn": float(churn_rate)}
        })

        return True
