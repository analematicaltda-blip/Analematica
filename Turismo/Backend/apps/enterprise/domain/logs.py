from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class DecisionLog(TenantAwareModel):
    """
    Enterprise decision history for EOS.
    """
    decision_type = models.CharField(max_length=100) # e.g., 'BUDGET_APPROVAL', 'EXPANSION_TRIGGER'
    input_payload = models.JSONField()
    output_result = models.JSONField()

    actor_id = models.CharField(max_length=100) # User or Agent
    reasoning = models.TextField(blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'enterprise'
        ordering = ['-timestamp']

class PolicyEvaluationLog(TenantAwareModel):
    """
    Record of every policy evaluation for traceability.
    """
    policy = models.ForeignKey('EnterprisePolicy', on_delete=models.CASCADE)
    metric_value = models.DecimalField(max_digits=20, decimal_places=2)
    was_breached = models.BooleanField()

    action_taken = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'enterprise'
