from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from apps.core_erp.base_models import BaseErpModel, TenantAwareModel

class EconomicNode(BaseErpModel):
    """
    Representa una entidad económica dentro del ecosistema holding.
    Puede ser una empresa del grupo, un proveedor estratégico o un partner.
    """
    NODE_TYPES = (
        ('OPERATIONAL', 'Operational Entity'),
        ('FINANCIAL', 'Financial Vehicle'),
        ('STRATEGIC', 'Strategic Partner'),
        ('EXTERNAL', 'External Market Interface'),
    )

    NODE_STATUS = (
        ('ACTIVE', 'Active & Integrated'),
        ('ISOLATED', 'Isolated (Risk Containment)'),
        ('SHOCK', 'Under Stress/Shock'),
        ('SUSPENDED', 'Suspended'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    entity_id = models.UUIDField(null=True, blank=True, help_text="ID of the LegalEntity or Company if internal")
    node_type = models.CharField(max_length=20, choices=NODE_TYPES, default='OPERATIONAL')
    status = models.CharField(max_length=20, choices=NODE_STATUS, default='ACTIVE')

    # Financial Metrics (Consolidated for Ecosystem Analysis)
    current_revenue = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    current_cost = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    capital_required = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    demand_forecast = models.DecimalField(max_digits=20, decimal_places=4, default=0)

    # Structural Data
    cost_structure = models.JSONField(default=dict, help_text="Breakdown of operational vs fixed costs")
    supply_dependencies = models.JSONField(default=list, help_text="List of critical supply nodes/external sources")

    # Ecosystem Scores
    risk_index = models.DecimalField(max_digits=5, decimal_places=4, default=0, help_text="0.0 to 1.0 risk level")
    efficiency_score = models.DecimalField(max_digits=5, decimal_places=4, default=1.0, help_text="0.0 to 1.0 performance level")
    systemic_importance = models.DecimalField(max_digits=5, decimal_places=4, default=0.5, help_text="Impact if this node fails")

    def __str__(self):
        return f"{self.name} ({self.node_type})"

class EconomicFlow(BaseErpModel):
    """
    Representa los flujos de recursos entre nodos del ecosistema.
    """
    FLOW_TYPES = (
        ('CAPITAL', 'Financial Capital'),
        ('GOODS', 'Physical Goods'),
        ('SERVICES', 'Operational Services'),
        ('INFORMATION', 'Strategic Intelligence'),
        ('INCENTIVE', 'Systemic Reward/Penalty'),
    )

    source_node = models.ForeignKey(EconomicNode, on_delete=models.CASCADE, related_name='outgoing_flows')
    target_node = models.ForeignKey(EconomicNode, on_delete=models.CASCADE, related_name='incoming_flows')
    flow_type = models.CharField(max_length=20, choices=FLOW_TYPES)
    value_per_period = models.DecimalField(max_digits=20, decimal_places=4)
    frequency = models.CharField(max_length=20, default='MONTHLY')
    is_active = models.BooleanField(default=True)

class InternalContract(BaseErpModel):
    """
    Gobierna la relación comercial y financiera entre nodos internos.
    Soporta microeconomía corporativa computacional.
    """
    PRICING_MODELS = (
        ('DYNAMIC', 'Dynamic Algorithm (EOE Driven)'),
        ('MARKUP', 'Cost Plus Markup'),
        ('FIXED', 'Fixed Agreement'),
        ('MARKET', 'External Market Reference'),
    )

    buyer = models.ForeignKey(EconomicNode, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(EconomicNode, on_delete=models.CASCADE, related_name='sales')
    pricing_model = models.CharField(max_length=20, choices=PRICING_MODELS, default='DYNAMIC')

    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    current_unit_price = models.DecimalField(max_digits=15, decimal_places=4, default=0)

    terms = models.JSONField(default=dict, help_text="SLAs, delivery terms, and penalties")
    performance_reward_multiplier = models.DecimalField(max_digits=5, decimal_places=4, default=1.1)
    performance_penalty_multiplier = models.DecimalField(max_digits=5, decimal_places=4, default=0.9)

class EcosystemIncentive(BaseErpModel):
    """
    Instrumentos de coordinación y alineación de incentivos.
    """
    node = models.ForeignKey(EconomicNode, on_delete=models.CASCADE, related_name='incentives')
    metric_linked = models.CharField(max_length=100, help_text="KPI used to trigger this incentive")
    threshold_value = models.DecimalField(max_digits=15, decimal_places=4)
    incentive_value = models.DecimalField(max_digits=15, decimal_places=4, help_text="Amount or token grant")
    is_tokenized = models.BooleanField(default=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, default='PENDING', choices=(
        ('PENDING', 'Pending Validation'),
        ('APPLIED', 'Applied & Executed'),
        ('REVOKED', 'Revoked'),
    ))
