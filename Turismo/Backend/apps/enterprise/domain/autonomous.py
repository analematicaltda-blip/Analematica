from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class LearningLoopRecord(TenantAwareModel):
    """
    Continuous Intelligence tracking for autonomous optimization.
    """
    engine_name = models.CharField(max_length=100)
    input_trend_data = models.JSONField()
    previous_rule_state = models.JSONField()
    suggested_rule_state = models.JSONField()

    impact_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    confidence_level = models.DecimalField(max_digits=5, decimal_places=4)

    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Learning Loop Record"

class AutonomousActionRecord(TenantAwareModel):
    """
    Detailed audit for every action executed at Autonomy Level > 1.
    """
    policy = models.ForeignKey('EnterprisePolicy', on_delete=models.CASCADE)
    autonomy_level = models.IntegerField()

    execution_payload = models.JSONField()
    outcome_status = models.CharField(max_length=50) # SUCCESS, FAILED, COMPENSATED

    correlation_id = models.UUIDField(db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'enterprise'

class CashOptimizationProposal(TenantAwareModel):
    """
    Output from the Autonomous Cash Management engine.
    """
    source_entity_id = models.UUIDField()
    target_entity_id = models.UUIDField()
    suggested_amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3)

    reasoning = models.TextField()
    priority = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=[('PENDING','Pending'), ('EXECUTED','Executed'), ('REJECTED','Rejected')], default='PENDING')

    class Meta:
        app_label = 'enterprise'

class SelfHealingAudit(TenantAwareModel):
    """
    Logs of automated remediation on the ledger or system state.
    """
    issue_type = models.CharField(max_length=100) # e.g., 'UNBALANCED_JOURNAL', 'ORPHANED_ENTRY'
    target_id = models.UUIDField()

    action_taken = models.CharField(max_length=255)
    result = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'enterprise'
