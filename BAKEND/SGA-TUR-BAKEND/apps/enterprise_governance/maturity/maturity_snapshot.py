from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class MaturitySnapshot(TenantAwareModel):
    """
    Periodic auditable record of the system's maturity state.
    """
    overall_score = models.FloatField()
    domain_breakdown = models.JSONField(help_text="Detailed scores per domain and category")

    gaps_detected = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)

    timestamp = models.DateTimeField(auto_now_add=True)

    integrity_hash = models.CharField(max_length=64, null=True, blank=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'enterprise_governance'
        verbose_name = "Maturity Snapshot"
        ordering = ['-timestamp']
