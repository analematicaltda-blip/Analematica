from .models import SaaSMetric, ChurnRiskScore, OperationalRiskIndex
from .metrics_engine import MetricsEngine
from django.db.models import Sum, Count
from decimal import Decimal
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class RiskScoringEngine:
    """
    Calculates the Global Operational Risk Index.
    """

    @staticmethod
    def calculate_global_risk():
        components = {}

        # 1. Revenue Concentration Risk
        # (Top customer revenue / Total revenue)
        total_revenue = SaaSMetric.objects.filter(metric_name='MRR_INFLOW').aggregate(total=Sum('value'))['total'] or Decimal('1')
        top_customer_revenue = SaaSMetric.objects.filter(metric_name='MRR_INFLOW').values('meta_data__customer_id').annotate(
            total=Sum('value')
        ).order_by('-total').first()

        if top_customer_revenue:
            concentration = (top_customer_revenue['total'] / total_revenue) * 100
            components['revenue_concentration'] = float(concentration)
        else:
            concentration = 0
            components['revenue_concentration'] = 0

        # 2. Churn Risk (High risk customer count)
        high_risk_customers = ChurnRiskScore.objects.filter(risk_level='HIGH').count()
        total_customers = ChurnRiskScore.objects.count() or 1
        churn_exposure = (high_risk_customers / total_customers) * 100
        components['churn_exposure'] = float(churn_exposure)

        # 3. Liquidity Risk (Billing vs Collection gap)
        total_billed = SaaSMetric.objects.filter(metric_name='TOTAL_BILLING').aggregate(total=Sum('value'))['total'] or Decimal('0')
        total_collected = SaaSMetric.objects.filter(metric_name='CASH_COLLECTED').aggregate(total=Sum('value'))['total'] or Decimal('0')

        if total_billed > 0:
            collection_gap = ((total_billed - total_collected) / total_billed) * 100
            components['liquidity_risk'] = float(collection_gap)
        else:
            components['liquidity_risk'] = 0

        # Overall Index (Weighted average)
        overall = (Decimal(str(concentration)) * Decimal('0.4')) + \
                  (Decimal(str(churn_exposure)) * Decimal('0.3')) + \
                  (Decimal(str(components['liquidity_risk'])) * Decimal('0.3'))

        recommendation = "Maintain healthy customer acquisition."
        if overall > 50:
            recommendation = "URGENT: Diversify customer base and improve collections."
        elif overall > 20:
            recommendation = "Monitor top customer dependency and churn signals."

        OperationalRiskIndex.objects.create(
            overall_index=min(overall, Decimal('100.00')),
            risk_components=components,
            recommendation=recommendation
        )

        return overall
