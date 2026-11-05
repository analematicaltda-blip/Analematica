from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from apps.core_erp.base_models import BaseErpModel

class StabilityCouncil(BaseErpModel):
    """
    Global Financial Stability Council (GFSC) - Phase 25.1.
    Órgano de supervisión técnica de riesgos sistémicos globales.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    authorized_jurisdictions = models.JSONField(default=list)

    is_active = models.BooleanField(default=True)
    last_stability_review = models.DateTimeField(null=True, blank=True)

    monitoring_status = models.CharField(max_length=10, choices=(
        ('GREEN', 'Normal Risk'),
        ('YELLOW', 'Rising Risk'),
        ('RED', 'Systemic Shock'),
    ), default='GREEN')

    def __str__(self):
        return self.name

class RiskAnalyticsNode(BaseErpModel):
    """
    Systemic Risk Analytics Grid (SRAG) - Phase 25.2.
    GRI = Sum(Exposure * Interconnectedness * Volatility)
    """
    council = models.ForeignKey(StabilityCouncil, on_delete=models.CASCADE, related_name='risk_nodes')
    region_code = models.CharField(max_length=10)

    exposure_value = models.DecimalField(max_digits=20, decimal_places=4)
    interconnectedness_score = models.DecimalField(max_digits=5, decimal_places=4)
    volatility_index = models.DecimalField(max_digits=5, decimal_places=4)

    node_risk_index = models.DecimalField(max_digits=5, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)

class LiquidityBuffer(BaseErpModel):
    """
    Liquidity Stabilization Network (LSN) - Phase 25.3.
    Buffers de liquidez pre-acordados y mecanismos de contingencia.
    """
    node = models.ForeignKey(RiskAnalyticsNode, on_delete=models.CASCADE, related_name='buffers')
    buffer_type = models.CharField(max_length=50, choices=(
        ('PRIVATE_INJECTION', 'Private Capital Injection'),
        ('CONTINGENT_LINE', 'Internal Contingency Line'),
        ('STABILIZATION_FUND', 'Regional Stabilization Buffer'),
    ))

    total_capacity = models.DecimalField(max_digits=25, decimal_places=4)
    available_liquidity = models.DecimalField(max_digits=25, decimal_places=4)

    activation_threshold = models.DecimalField(max_digits=5, decimal_places=4, help_text="Liquidity Stress Level to trigger")
    is_locked = models.BooleanField(default=False)

class ShockAbsorptionPolicy(BaseErpModel):
    """
    Capital Shock Absorption Framework (CSAF) - Phase 25.4.
    Impact = Magnitude * NetworkDensity
    """
    name = models.CharField(max_length=255)
    strategy_type = models.CharField(max_length=50, choices=(
        ('DIVERSIFICATION', 'Automatic Exposure Diversification'),
        ('DECOUPLING', 'Temporal Node Decoupling'),
        ('SEGMENTATION', 'Preventive Sectorial Segmentation'),
    ))

    target_network_density = models.DecimalField(max_digits=5, decimal_places=4)
    is_active = models.BooleanField(default=True)

    execution_params = models.JSONField(default=dict)

class CrisisCase(BaseErpModel):
    """
    Crisis Containment & Segmentation Protocol - Phase 25.5.
    Epicenter identification and automated isolation.
    """
    epicenter_node = models.ForeignKey(RiskAnalyticsNode, on_delete=models.CASCADE)
    crisis_magnitude = models.DecimalField(max_digits=10, decimal_places=4)

    containment_status = models.CharField(max_length=20, default='IDENTIFIED', choices=(
        ('IDENTIFIED', 'Epicenter Identified'),
        ('ISOLATING', 'Active Segmentation'),
        ('CONTAINED', 'Contagion Stopped'),
        ('RESOLVED', 'Stability Restored'),
    ))

    isolated_nodes_count = models.IntegerField(default=0)
    time_to_containment = models.DurationField(null=True, blank=True)
    resolution_report = models.TextField(blank=True)
