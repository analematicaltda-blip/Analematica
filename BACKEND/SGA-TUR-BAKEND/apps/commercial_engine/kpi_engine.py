import logging
from django.db.models import Sum
from .models import SaaSSubscription, CommercialKPI, SaaSLead
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class KPIEngine:
    """
    Calcula y almacena métricas comerciales en tiempo real.
    """

    @classmethod
    def update_mrr(cls):
        """Calcula el Monthly Recurring Revenue actual."""
        total_mrr = SaaSSubscription.objects.filter(status='ACTIVE').aggregate(Sum('mrr'))['mrr__sum'] or 0
        CommercialKPI.objects.create(metric_name='MRR', value=total_mrr)
        CommercialKPI.objects.create(metric_name='ARR', value=total_mrr * 12)
        logger.info(f"KPI Updated: MRR={total_mrr}")
        return total_mrr

    @classmethod
    def calculate_conversion_rate(cls):
        """Calcula la tasa de conversión de leads a clientes."""
        total_leads = SaaSLead.objects.count()
        if total_leads == 0: return 0

        converted_leads = SaaSLead.objects.filter(status=SaaSLead.Status.CONVERTED).count()
        rate = (converted_leads / total_leads) * 100
        CommercialKPI.objects.create(metric_name='CONVERSION_RATE', value=rate)
        return rate

    @classmethod
    def handle_subscription_activated(cls, payload):
        """Subscriber para SUBSCRIPTION_ACTIVATED"""
        cls.update_mrr()
        cls.calculate_conversion_rate()

    @classmethod
    def handle_lead_converted(cls, payload):
        """Subscriber para LEAD_CONVERTED"""
        cls.calculate_conversion_rate()

# Los registros en el EventBus se harán en el AppConfig
