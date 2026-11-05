from .plan_model import SaaSPlan
from .lead_model import SaaSLead
import uuid
from django.db import models
from apps.core_erp.base_models import BaseInvoice, BaseInvoiceLine

class SaaSSubscription(models.Model):
    class Status(models.TextChoices):
        TRIAL = 'TRIAL', 'Trial'
        ACTIVE = 'ACTIVE', 'Active'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        CANCELLED = 'CANCELLED', 'Cancelled'

    class BillingCycle(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly'
        ANNUAL = 'ANNUAL', 'Annual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(unique=True, db_index=True) # Reference to core_erp Company
    plan = models.ForeignKey(SaaSPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    start_date = models.DateField(auto_now_add=True)
    renewal_date = models.DateField()
    billing_cycle = models.CharField(max_length=20, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)

    mrr = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='COP')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company_id} - {self.plan.name} ({self.status})"

class UsageEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(db_index=True)
    metric_type = models.CharField(max_length=50, db_index=True)
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

class UsageAggregation(models.Model):
    subscription = models.ForeignKey(SaaSSubscription, on_delete=models.CASCADE)
    metric_type = models.CharField(max_length=50)
    total_quantity = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    period_start = models.DateField()
    period_end = models.DateField()
    is_billed = models.BooleanField(default=False)

class LeadPipelineLog(models.Model):
    """
    Rastreo histórico de transiciones en el Pipeline para auditoría y métricas de velocidad.
    """
    lead = models.ForeignKey(SaaSLead, on_delete=models.CASCADE, related_name='pipeline_logs')
    from_status = models.CharField(max_length=50)
    to_status = models.CharField(max_length=50)
    changed_at = models.DateTimeField(auto_now_add=True)
    duration_in_stage_hours = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.lead.company_name}: {self.from_status} -> {self.to_status}"

class SaaSInvoice(BaseInvoice):
    """
    Factura de suscripción SaaS generada por la Holding.
    """
    subscription = models.ForeignKey(SaaSSubscription, on_delete=models.PROTECT, related_name='invoices')
    company_id = models.UUIDField(db_index=True) # ID del inquilino (cliente)

    class Meta:
        app_label = 'commercial_engine'

class CustomerHealthIndex(models.Model):
    """
    EOS Activation: Integrated health index for churn prediction.
    Integrates Usage, Support, Billing, and Churn Risk.
    """
    company_id = models.UUIDField(unique=True, db_index=True)
    health_score = models.FloatField(help_text="0.0 to 100.0")

    usage_component = models.FloatField()
    billing_component = models.FloatField()
    churn_risk_component = models.FloatField()

    last_updated = models.DateTimeField(auto_now=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'commercial_engine'
        verbose_name = "Customer Health Index"

class CommercialKPI(models.Model):
    """
    Snapshots de métricas clave para el dashboard estratégico.
    """
    metric_name = models.CharField(max_length=50, db_index=True) # MRR, ARR, CAC, LTV
    value = models.DecimalField(max_digits=18, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'commercial_engine'
        ordering = ['-timestamp']
        verbose_name = "Factura SaaS"

class SaaSInvoiceLine(BaseInvoiceLine):
    invoice = models.ForeignKey(SaaSInvoice, on_delete=models.CASCADE, related_name='lines')

    class Meta:
        app_label = 'commercial_engine'
