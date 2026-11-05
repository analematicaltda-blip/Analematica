from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class EnterpriseWorkflow(TenantAwareModel):
    class Status(models.TextChoices):
        PLANNED = 'PLANNED', 'Planned'
        RUNNING = 'RUNNING', 'Running'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        COMPENSATING = 'COMPENSATING', 'Compensating'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLANNED)

    context_data = models.JSONField(default=dict, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Enterprise Workflow"

class WorkflowStep(TenantAwareModel):
    workflow = models.ForeignKey(EnterpriseWorkflow, on_delete=models.CASCADE, related_name='steps')
    order = models.PositiveIntegerField()
    name = models.CharField(max_length=255)

    target_domain = models.CharField(max_length=100) # e.g., 'FINANCE', 'OPERATIONS'
    action_name = models.CharField(max_length=255)

    params = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, default='PENDING')

    error_log = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'enterprise'
        ordering = ['order']
