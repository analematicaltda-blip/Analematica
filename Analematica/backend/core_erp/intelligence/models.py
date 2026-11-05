from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class FinancialProjection(TenantAwareModel):
    """
    Blueprint Alignment: Forecasted financial metrics.
    """
    projection_type = models.CharField(max_length=50) # REVENUE, CASHFLOW, CHURN
    target_date = models.DateField()
    predicted_value = models.DecimalField(max_digits=18, decimal_places=2)
    confidence_interval_low = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    confidence_interval_high = models.DecimalField(max_digits=18, decimal_places=2, null=True)
    model_version = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Financial Projection"

class SimulationScenario(TenantAwareModel):
    """
    Blueprint Alignment: 'What-if' strategic scenarios.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    parameters = models.JSONField() # e.g. {"tax_increase": 0.05, "fx_drop": 0.10}
    results = models.JSONField(null=True) # Projected impact
    created_by = models.CharField(max_length=100)

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Simulation Scenario"
