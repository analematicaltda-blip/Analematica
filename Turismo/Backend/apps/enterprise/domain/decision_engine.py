from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class RiskExposure(TenantAwareModel):
    class RiskType(models.TextChoices):
        FINANCIAL = 'FINANCIAL', 'Financial Liquidity'
        FISCAL = 'FISCAL', 'Fiscal Compliance'
        FX = 'FX', 'Currency Exposure'
        CONCENTRATION = 'CONCENTRATION', 'Revenue Concentration'
        COUNTRY = 'COUNTRY', 'Country Risk'

    risk_type = models.CharField(max_length=50, choices=RiskType.choices)
    exposure_value = models.DecimalField(max_digits=20, decimal_places=2)
    risk_level = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')])

    factors = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Risk Exposure"

class EnterpriseDecisionRule(TenantAwareModel):
    trigger_metric = models.CharField(max_length=100) # e.g. 'CASH_RUNWAY'
    condition = models.CharField(max_length=10, choices=[('LT', '<'), ('GT', '>'), ('LTE', '<='), ('GTE', '>=')])
    threshold = models.DecimalField(max_digits=20, decimal_places=2)

    recommended_action = models.CharField(max_length=255)
    auto_execute = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Decision Rule"
