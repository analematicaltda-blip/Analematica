from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class EnterprisePolicy(TenantAwareModel):
    class Scope(models.TextChoices):
        TENANT = 'TENANT', 'Tenant'
        ENTITY = 'ENTITY', 'Legal Entity'
        HOLDING = 'HOLDING', 'Holding'
        GLOBAL = 'GLOBAL', 'Global System'

    class Action(models.TextChoices):
        ALERT = 'ALERT', 'Trigger Alert'
        BLOCK = 'BLOCK', 'Block Operation'
        ESCALATE = 'ESCALATE', 'Escalate to CFO'
        ADJUST_BUDGET = 'ADJUST_BUDGET', 'Adjust Budget'
        WORKFLOW = 'WORKFLOW', 'Trigger Corrective Workflow'
        OPTIMIZE = 'OPTIMIZE', 'Self-Optimize Policy'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    scope = models.CharField(max_length=50, choices=Scope.choices, default=Scope.TENANT)

    metric_name = models.CharField(max_length=100, help_text="KPI name to monitor (e.g., EBITDA_MARGIN)")
    threshold = models.DecimalField(max_digits=20, decimal_places=2)
    operator = models.CharField(max_length=10, choices=[('GT','>'), ('LT','<'), ('EQ','=='), ('GTE','>='), ('LTE','<=')])

    action_on_breach = models.CharField(max_length=50, choices=Action.choices, default=Action.ALERT)
    action_params = models.JSONField(default=dict, blank=True)

    # Phase 9: Autonomous Enterprise
    autonomy_level = models.IntegerField(default=0, help_text="0: Alert, 1: Recommend, 2: Execute (Confirm), 3: Auto-Execute, 4: Adjust Rules, 5: Strategic Optimization")
    dynamic_threshold_model = models.CharField(max_length=100, blank=True, null=True, help_text="ML model name for dynamic thresholds")
    escalation_matrix = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Enterprise Policy"

    def __str__(self):
        return f"{self.name} ({self.scope})"
