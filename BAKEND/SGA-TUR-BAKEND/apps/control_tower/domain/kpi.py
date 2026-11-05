from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class KPI(TenantAwareModel):
    class MetricType(models.TextChoices):
        FINANCIAL = 'FINANCIAL', 'Financial'
        OPERATIONAL = 'OPERATIONAL', 'Operational'
        STRATEGIC = 'STRATEGIC', 'Strategic'
        TECHNICAL = 'TECHNICAL', 'Technical'

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=MetricType.choices)
    value = models.DecimalField(max_digits=20, decimal_places=2)
    unit = models.CharField(max_length=20, default='USD')

    # Context
    legal_entity_id = models.UUIDField(null=True, blank=True)
    country_code = models.CharField(max_length=3, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    meta_data = models.JSONField(default=dict, blank=True)

    # Versioning for thresholds or methodology
    methodology_version = models.CharField(max_length=50, default="v1.0")

    class Meta:
        app_label = 'control_tower'
        verbose_name = "KPI Snapshot"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.name}: {self.value} {self.unit} ({self.timestamp})"
