from django.db import models
import uuid
from django.utils import timezone

class AutonomousAgent(models.Model):
    AUTONOMY_LEVELS = [
        ('ADVISORY', 'Advisory'),
        ('SUPERVISED', 'Supervised'),
        ('AUTOMATIC', 'Automatic'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('SANDBOX', 'Sandbox'),
    ]
    RISK_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent_code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=50) # pricing, churn, marketing, cashflow
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SANDBOX')
    autonomy_level = models.CharField(max_length=20, choices=AUTONOMY_LEVELS, default='ADVISORY')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='LOW')
    last_execution = models.DateTimeField(null=True, blank=True)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00) # 0.00 to 100.00
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.agent_code})"

class PolicyRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=50, unique=True)
    description = models.TextField()
    parameters = models.JSONField(default=dict) # e.g., {"max_discount": 0.15, "min_margin": 0.20}
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class DecisionProposal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('BLOCKED', 'Blocked'),
        ('EXECUTED', 'Executed'),
        ('FAILED', 'Failed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(AutonomousAgent, on_delete=models.CASCADE, related_name='proposals')
    target_entity_id = models.UUIDField() # ID of Company, Customer, or Plan
    target_entity_type = models.CharField(max_length=50)
    proposed_action = models.CharField(max_length=100) # e.g., 'APPLY_DISCOUNT', 'ADJUST_PRICE'
    action_parameters = models.JSONField(default=dict)
    expected_impact = models.JSONField(default=dict) # e.g., {"churn_reduction": 0.05}
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_notes = models.TextField(blank=True)

class AutonomousAction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.OneToOneField(DecisionProposal, on_delete=models.CASCADE, related_name='executed_action')
    executed_at = models.DateTimeField(default=timezone.now)
    execution_hash = models.CharField(max_length=64, unique=True)
    result_data = models.JSONField(default=dict)
    is_reverted = models.BooleanField(default=False)
    reversion_data = models.JSONField(null=True, blank=True)
    reverted_at = models.DateTimeField(null=True, blank=True)

class AgentExecutionAudit(models.Model):
    STEPS = [
        ('METRIC', 'Metric Signal'),
        ('DECISION', 'Decision Proposal'),
        ('POLICY', 'Policy Validation'),
        ('ACTION', 'Action Execution'),
        ('RESULT', 'Result Measurement'),
        ('LEARNING', 'Learning Adjustment'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now)
    agent_code = models.CharField(max_length=50)
    step = models.CharField(max_length=20, choices=STEPS)
    related_id = models.UUIDField(null=True, blank=True) # ID of proposal or action
    data = models.JSONField()
    success = models.BooleanField(default=True)

class Experiment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    control_group = models.JSONField(default=list) # List of entity IDs
    test_group = models.JSONField(default=list)
    metrics_to_track = models.JSONField(default=list)
    results = models.JSONField(default=dict)
