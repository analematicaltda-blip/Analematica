from django.db import models
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from .models import SaaSMetric, IntelligenceAuditLog
from decimal import Decimal
import logging
import time

logger = logging.getLogger(__name__)

class MetricsEngine:
    """
    Calculates advanced SaaS metrics from the Data Mart.
    """

    @staticmethod
    def calculate_all():
        start_time = time.time()
        metrics = {}

        metrics['mrr'] = float(MetricsEngine.calculate_mrr())
        metrics['arr'] = float(metrics['mrr'] * 12)
        metrics['arpu'] = float(MetricsEngine.calculate_arpu())
        metrics['churn_rate'] = float(MetricsEngine.calculate_churn_rate())

        # Net Revenue Retention (NRR) - Simplified for MVP
        metrics['nrr'] = float(MetricsEngine.calculate_nrr())

        # Audit the calculation
        execution_time = int((time.time() - start_time) * 1000)
        IntelligenceAuditLog.objects.create(
            engine_name='MetricsEngine',
            input_dataset_hash='N/A',
            output_result_summary=metrics,
            execution_time_ms=execution_time
        )

        return metrics

    @staticmethod
    def calculate_mrr():
        # MRR = Sum(MRR_INFLOW) + Sum(MRR_EXPANSION) - Sum(MRR_CONTRACTION) - Sum(MRR_CHURN)
        inflow = SaaSMetric.objects.filter(metric_name='MRR_INFLOW').aggregate(total=Sum('value'))['total'] or Decimal('0.00')
        expansion = SaaSMetric.objects.filter(metric_name='MRR_EXPANSION').aggregate(total=Sum('value'))['total'] or Decimal('0.00')
        contraction = SaaSMetric.objects.filter(metric_name='MRR_CONTRACTION').aggregate(total=Sum('value'))['total'] or Decimal('0.00')
        churn = SaaSMetric.objects.filter(metric_name='MRR_CHURN').aggregate(total=Sum('value'))['total'] or Decimal('0.00')
        return inflow + expansion - contraction - churn

    @staticmethod
    def calculate_arpu():
        # ARPU = MRR / Active Customers
        mrr = MetricsEngine.calculate_mrr()
        customer_count = SaaSMetric.objects.filter(metric_name='MRR_INFLOW').values('meta_data__customer_id').distinct().count()
        if customer_count > 0:
            return mrr / Decimal(customer_count)
        return Decimal('0.00')

    @staticmethod
    def calculate_churn_rate():
        # Monthly Churn = (Customers Lost / Customers at Start)
        # Simplified: (MRR Churn in last 30 days / Total MRR)
        last_30_days = timezone.now() - timezone.timedelta(days=30)
        churn_30 = SaaSMetric.objects.filter(metric_name='MRR_CHURN', timestamp__gte=last_30_days).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
        total_mrr = MetricsEngine.calculate_mrr()

        if total_mrr > 0:
            return (churn_30 / total_mrr) * 100
        return Decimal('0.00')

    @staticmethod
    def calculate_nrr():
        # NRR = (Beginning MRR + Expansion - Contraction - Churn) / Beginning MRR
        # For simplicity, we use MRR from 30 days ago as Beginning MRR
        last_30_days = timezone.now() - timezone.timedelta(days=30)

        beg_mrr = SaaSMetric.objects.filter(timestamp__lt=last_30_days).aggregate(
            total=Sum('value', filter=models.Q(metric_name='MRR_INFLOW')) +
                  Sum('value', filter=models.Q(metric_name='MRR_EXPANSION')) -
                  Sum('value', filter=models.Q(metric_name='MRR_CONTRACTION')) -
                  Sum('value', filter=models.Q(metric_name='MRR_CHURN'))
        )['total'] or Decimal('0.00')

        if beg_mrr <= 0:
            # If no historical MRR, use current MRR or 100%
            return Decimal('100.00')

        expansion = SaaSMetric.objects.filter(metric_name='MRR_EXPANSION', timestamp__gte=last_30_days).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
        contraction = SaaSMetric.objects.filter(metric_name='MRR_CONTRACTION', timestamp__gte=last_30_days).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
        churn = SaaSMetric.objects.filter(metric_name='MRR_CHURN', timestamp__gte=last_30_days).aggregate(total=Sum('value'))['total'] or Decimal('0.00')

        nrr = ((beg_mrr + expansion - contraction - churn) / beg_mrr) * 100
        return nrr

    @staticmethod
    def calculate_cac_ltv():
        # Placeholder for unit economics
        return {"cac": Decimal("50.00"), "ltv": Decimal("500.00")}
