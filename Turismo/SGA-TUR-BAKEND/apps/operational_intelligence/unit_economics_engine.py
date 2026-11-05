from .models import SaaSMetric, UnitEconomics
from .metrics_engine import MetricsEngine
from django.db.models import Sum, Avg
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class UnitEconomicsEngine:
    """
    Calculates LTV, CAC, and ROI per customer.
    """

    @staticmethod
    def calculate_all():
        customers = SaaSMetric.objects.values_list('meta_data__customer_id', flat=True).distinct()

        for customer_id in customers:
            if not customer_id: continue
            UnitEconomicsEngine.calculate_for_customer(customer_id)

    @staticmethod
    def calculate_for_customer(customer_id):
        customer_id_str = str(customer_id)
        # 1. CAC (Customer Acquisition Cost)
        # Placeholder: ideally linked to UTM campaign costs
        # For now, use a flat estimate or random variation
        cac = Decimal('150.00')

        # 2. LTV (Lifetime Value)
        # LTV = ARPU * Gross Margin / Churn Rate
        # Or simplified: Sum of all revenue from this customer
        total_revenue = SaaSMetric.objects.filter(
            meta_data__customer_id=customer_id_str,
            metric_name__in=['MRR_INFLOW', 'MRR_EXPANSION', 'USAGE_REVENUE']
        ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')

        # 3. Cost to Serve (Infrastructure + IA)
        # Use USAGE_UNITS as a base
        usage_units = SaaSMetric.objects.filter(
            meta_data__customer_id=customer_id_str,
            metric_name='USAGE_UNITS'
        ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')

        # Assume 0.05 per unit cost
        cost_to_serve = usage_units * Decimal('0.05') + Decimal('10.00') # Base cost 10

        # 4. Gross Margin
        if total_revenue > 0:
            gross_margin = ((total_revenue - cost_to_serve) / total_revenue) * 100
        else:
            gross_margin = Decimal('0.00')

        # 5. Payback Period
        monthly_profit = (total_revenue / Decimal('12')) * (gross_margin / 100) # Assumes 1 year of data
        if monthly_profit > 0:
            payback = cac / monthly_profit
        else:
            payback = Decimal('0.00')

        UnitEconomics.objects.update_or_create(
            customer_id=customer_id,
            defaults={
                'cac': cac,
                'ltv': total_revenue * 3, # Projected LTV (3x current for MVP)
                'gross_margin': max(min(gross_margin, Decimal('100.00')), Decimal('0.00')),
                'cost_to_serve': cost_to_serve,
                'payback_period_months': payback
            }
        )

        return True
