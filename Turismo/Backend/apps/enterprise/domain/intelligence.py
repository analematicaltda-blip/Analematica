from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class ScenarioSimulation(TenantAwareModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Parameters
    revenue_growth_rate = models.DecimalField(max_digits=5, decimal_places=4, help_text="e.g. 0.05 for 5%")
    fx_variation = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    cost_inflation = models.DecimalField(max_digits=5, decimal_places=4, default=0)

    # Projected Results (Summary)
    projected_ebitda = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    projected_cash_position = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Scenario Simulation"

class RollingForecast(TenantAwareModel):
    fiscal_year = models.IntegerField()
    month = models.IntegerField()

    base_budget_revenue = models.DecimalField(max_digits=20, decimal_places=2)
    actual_revenue_mtd = models.DecimalField(max_digits=20, decimal_places=2)

    projected_variance = models.DecimalField(max_digits=20, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Rolling Forecast"
