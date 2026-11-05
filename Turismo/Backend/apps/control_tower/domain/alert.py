from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class Alert(TenantAwareModel):
    class Severity(models.TextChoices):
        INFO = 'INFO', 'Informational'
        PREVENTIVE = 'PREVENTIVE', 'Preventive'
        CRITICAL = 'CRITICAL', 'Critical'
        BLOCKING = 'BLOCKING', 'Blocking'

    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        ACKNOWLEDGED = 'ACKNOWLEDGED', 'Acknowledged'
        RESOLVED = 'RESOLVED', 'Resolved'
        ESCALATED = 'ESCALATED', 'Escalated'

    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.INFO)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    title = models.CharField(max_length=255)
    description = models.TextField()

    # Scope
    entity_scope = models.CharField(max_length=50, default='TENANT') # TENANT, HOLDING, GLOBAL

    source_event = models.CharField(max_length=100, null=True, blank=True)
    correlation_id = models.UUIDField(null=True, blank=True)

    # Severity Classification Engine enhancements
    impact_score = models.FloatField(default=0.0, help_text="Estimated impact 0-100")
    domain_affected = models.CharField(max_length=100, null=True, blank=True)
    financial_exposure = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    confidence_score = models.FloatField(default=0.95)

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'control_tower'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.severity}] {self.title} - {self.status}"
