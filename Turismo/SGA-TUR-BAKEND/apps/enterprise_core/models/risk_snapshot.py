from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class RiskSnapshot(TenantAwareModel):
    """
    Periodic or event-driven snapshot of systemic risk exposure.
    """
    overall_score = models.FloatField(help_text="Normalized risk 0.0 to 1.0")
    risk_factors = models.JSONField(help_text="Breakdown of contributors (liquidity, concentration, churn, etc.)")

    timestamp = models.DateTimeField(auto_now_add=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'enterprise_core'
        verbose_name = "Risk Snapshot"
        verbose_name_plural = "Risk Snapshots"
        ordering = ['-timestamp']
