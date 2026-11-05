from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class StrategicRule(TenantAwareModel):
    """
    Formal definition of a strategic decision rule.
    Standardized to Technical English and UUID v4 (Schema v2.1).
    """
    trigger_metric = models.CharField(max_length=100, help_text="Metric name from control_tower or operational_intelligence")
    condition_expression = models.CharField(max_length=255, help_text="Logic expression e.g. 'metric < 1000'")
    risk_weight = models.FloatField(default=1.0, help_text="Impact of this rule on overall risk score")
    recommended_action = models.CharField(max_length=255, help_text="Intent name to be executed via GovernanceKernel")

    # Phase 5: Autonomy Levels
    autonomy_level = models.IntegerField(default=1, help_text="0: Suggestion, 1: Human Approval, 2: Auto under Threshold, 3: Full Autonomy")
    impact_threshold = models.DecimalField(max_digits=20, decimal_places=2, default=1000.00, help_text="Max financial impact for auto-execution")

    is_active = models.BooleanField(default=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'enterprise_core'
        verbose_name = "Strategic Rule"
        verbose_name_plural = "Strategic Rules"

    def __str__(self):
        return f"Rule: {self.trigger_metric} ({self.condition_expression})"
