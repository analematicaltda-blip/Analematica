from django.db import models
import uuid
from django.utils.timezone import now

class SaaSMetric(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=now)
    metric_name = models.CharField(max_length=100)  # e.g., 'MRR', 'ARR', 'LTV'
    value = models.DecimalField(max_digits=20, decimal_places=2)
    dimension = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'Total', 'Plan: Premium'
    meta_data = models.JSONField(default=dict)

    class Meta:
        verbose_name = "SaaS Metric"
        verbose_name_plural = "SaaS Metrics"
        ordering = ['-timestamp']

class CohortAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    acquisition_month = models.DateField()
    cohort_size = models.IntegerField()
    metric_name = models.CharField(max_length=100)
    month_number = models.IntegerField()  # 0, 1, 2... months after acquisition
    value = models.DecimalField(max_digits=20, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

class ChurnRiskScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField()  # Links to ProviderProfile or Company
    risk_score = models.DecimalField(max_digits=5, decimal_places=2)  # 0 to 100
    risk_level = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')])
    factors = models.JSONField(default=dict)  # e.g., {"usage_drop": 0.4, "late_payments": 2}
    calculated_at = models.DateTimeField(auto_now=True)

class RevenueForecast(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forecast_date = models.DateField()
    projected_revenue = models.DecimalField(max_digits=20, decimal_places=2)
    projected_cashflow = models.DecimalField(max_digits=20, decimal_places=2)
    confidence_interval = models.DecimalField(max_digits=5, decimal_places=2)

    # Explainability Layer
    variables_used = models.JSONField(default=dict)
    weight_estimation = models.JSONField(default=dict)

    algorithm_version = models.CharField(max_length=50)
    dataset_reference = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    __schema_version__ = "v2.1"

class UnitEconomics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.UUIDField()
    cac = models.DecimalField(max_digits=20, decimal_places=2)
    ltv = models.DecimalField(max_digits=20, decimal_places=2)
    gross_margin = models.DecimalField(max_digits=5, decimal_places=2)
    cost_to_serve = models.DecimalField(max_digits=20, decimal_places=2)
    payback_period_months = models.DecimalField(max_digits=10, decimal_places=2)
    last_calculated = models.DateTimeField(auto_now=True)

class OperationalRiskIndex(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=now)
    overall_index = models.DecimalField(max_digits=5, decimal_places=2)
    risk_components = models.JSONField(default=dict)  # concentration, liquidity, churn_trend
    recommendation = models.TextField()

class IntelligenceAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    engine_name = models.CharField(max_length=100)

    # Model Maturity Metrics
    model_version = models.CharField(max_length=50, default="1.0.0")
    accuracy_score = models.FloatField(null=True, blank=True)

    input_dataset_hash = models.CharField(max_length=64)
    output_result_summary = models.JSONField()
    execution_time_ms = models.IntegerField()

    __schema_version__ = "v2.1"
