from .models import SaaSMetric, CohortAnalysis
from django.db.models import Sum, Count, Min
from django.utils import timezone
from decimal import Decimal
import datetime

class CohortEngine:
    """
    Groups customers by acquisition month and analyzes retention/LTV.
    """

    @staticmethod
    def run_analysis():
        # 1. Identify acquisition month for each customer
        acquisitions = SaaSMetric.objects.filter(metric_name='MRR_INFLOW').values('meta_data__customer_id').annotate(
            first_seen=Min('timestamp')
        )

        cohort_map = {}
        for acq in acquisitions:
            cust_id = acq['meta_data__customer_id']
            month = acq['first_seen'].replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()
            if month not in cohort_map:
                cohort_map[month] = []
            cohort_map[month].append(cust_id)

        # 2. For each cohort, calculate metrics over time
        for month, customers in cohort_map.items():
            cohort_size = len(customers)

            # Month 0 retention
            CohortAnalysis.objects.update_or_create(
                acquisition_month=month,
                month_number=0,
                metric_name='RETENTION_COUNT',
                defaults={'cohort_size': cohort_size, 'value': Decimal(cohort_size)}
            )

            # Analyze subsequent months
            now = timezone.now().date()
            current_month = month
            month_count = 1

            while True:
                # Advance one month
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)

                if current_month > now:
                    break

                # Count active customers in this cohort for this month
                # Active if they had an INFLOW and NO CHURN since then (simplified)
                active_count = 0
                for cust_id in customers:
                    has_churned = SaaSMetric.objects.filter(
                        metric_name='MRR_CHURN',
                        meta_data__customer_id=str(cust_id),
                        timestamp__date__lt=current_month
                    ).exists()
                    if not has_churned:
                        active_count += 1

                CohortAnalysis.objects.update_or_create(
                    acquisition_month=month,
                    month_number=month_count,
                    metric_name='RETENTION_COUNT',
                    defaults={'cohort_size': cohort_size, 'value': Decimal(active_count)}
                )
                month_count += 1

        return True
