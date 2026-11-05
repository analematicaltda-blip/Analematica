from .models import SaaSMetric, ChurnRiskScore
from apps.core_erp.event_bus import EventBus
from django.db.models import Sum, Avg
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ChurnEngine:
    """
    Predicts churn risk based on real data signals.
    """

    @staticmethod
    def evaluate_all_customers():
        # Get all unique customer IDs
        customers = SaaSMetric.objects.values_list('meta_data__customer_id', flat=True).distinct()

        for customer_id in customers:
            if not customer_id: continue
            ChurnEngine.evaluate_customer(customer_id)

    @staticmethod
    def evaluate_customer(customer_id):
        risk_score = Decimal('0.00')
        factors = {}
        customer_id_str = str(customer_id)

        # 1. Signal: Usage Drop
        # Compare usage in last 7 days vs previous 7 days
        now = timezone.now()
        usage_last_7 = SaaSMetric.objects.filter(
            metric_name='USAGE_UNITS',
            meta_data__customer_id=customer_id_str,
            timestamp__gte=now - timezone.timedelta(days=7)
        ).aggregate(total=Sum('value'))['total'] or Decimal('0')

        usage_prev_7 = SaaSMetric.objects.filter(
            metric_name='USAGE_UNITS',
            meta_data__customer_id=customer_id_str,
            timestamp__lt=now - timezone.timedelta(days=7),
            timestamp__gte=now - timezone.timedelta(days=14)
        ).aggregate(total=Sum('value'))['total'] or Decimal('0')

        if usage_prev_7 > 0:
            drop_ratio = (usage_prev_7 - usage_last_7) / usage_prev_7
            if drop_ratio > 0.3: # More than 30% drop
                impact = drop_ratio * 40 # Up to 40 points
                risk_score += impact
                factors['usage_drop'] = float(drop_ratio)

        # 2. Signal: Late Payments
        # Count unpaid invoices past due date (placeholder, depends on Invoice status)
        # For now, use a simplified metric: any USAGE_BILLED without PAYMENT_RECONCILED in meta_data
        # (This is just a proxy for this phase)
        unpaid_count = SaaSMetric.objects.filter(
            metric_name='TOTAL_BILLING',
            meta_data__payload__customer_id=customer_id_str,
            # Simplified: if we have more BILLING than COLLECTED for this customer
        ).count() # This is too simplistic, but good enough for a score trigger

        # Let's assume 10 points per "potential" issue
        # risk_score += Decimal('10.00') # Placeholder factor

        # 3. Final Classification
        risk_level = 'LOW'
        if risk_score > 70:
            risk_level = 'HIGH'
        elif risk_score > 30:
            risk_level = 'MEDIUM'

        ChurnRiskScore.objects.update_or_create(
            customer_id=customer_id,
            defaults={
                'risk_score': min(risk_score, Decimal('100.00')),
                'risk_level': risk_level,
                'factors': factors
            }
        )

        if risk_level == 'HIGH':
            EventBus.emit('CHURN_RISK_ALERT', {
                'customer_id': str(customer_id),
                'risk_score': float(risk_score),
                'factors': factors
            })

        return risk_score
