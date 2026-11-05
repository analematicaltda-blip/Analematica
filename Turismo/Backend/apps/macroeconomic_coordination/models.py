from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from apps.core_erp.base_models import BaseErpModel

class MacroCouncil(BaseErpModel):
    """
    Strategic Macroeconomic Council (SMC) - Phase 24.1.
    Órgano estratégico para coordinar información y respuesta técnica Holding-Estado.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    jurisdiction_scope = models.JSONField(default=list, help_text="Participating states/regions")

    technical_members = models.JSONField(default=list, help_text="State and Holding technical reps")
    is_active = models.BooleanField(default=True)

    coordination_level = models.IntegerField(choices=(
        (1, 'Passive Monitoring'),
        (2, 'Technical Coordination'),
        (3, 'Strategic Crisis Coordination'),
    ), default=1)

    def __str__(self):
        return self.name

class SystemicRiskIndicator(BaseErpModel):
    """
    Systemic Risk Observatory (SRO) - Phase 24.2.
    SR = f(LiquidityShock, CapitalVolatility, Interconnectedness, Leverage)
    """
    council = models.ForeignKey(MacroCouncil, on_delete=models.CASCADE, related_name='risk_indicators')
    indicator_name = models.CharField(max_length=100)

    liquidity_shock_factor = models.DecimalField(max_digits=5, decimal_places=4)
    capital_volatility_index = models.DecimalField(max_digits=5, decimal_places=4)
    interconnectedness_score = models.DecimalField(max_digits=5, decimal_places=4)
    leverage_ratio = models.DecimalField(max_digits=5, decimal_places=4)

    net_systemic_risk = models.DecimalField(max_digits=5, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)

class CapitalCoordinationNode(BaseErpModel):
    """
    Liquidity & Capital Coordination Engine - Phase 24.3.
    Maneja flujos de capital simulados y buffers preventivos.
    """
    name = models.CharField(max_length=255)
    monetary_interface = models.CharField(max_length=10, help_text="Target currency (e.g., USD, COP)")

    current_private_buffer = models.DecimalField(max_digits=25, decimal_places=4, default=0)
    required_stabilization_buffer = models.DecimalField(max_digits=25, decimal_places=4, default=0)

    last_flow_simulation_hash = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, default='STABLE')

class EconomicModelSnapshot(BaseErpModel):
    """
    Predictive Economic Modeling Layer - Phase 24.4.
    Registra snapshots de modelos macro (DSGE, Agent-Based).
    """
    snapshot_name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=50, choices=(
        ('DSGE_EXTENDED', 'Dynamic Stochastic General Equilibrium'),
        ('AGENT_BASED', 'Agent-Based Macro Simulation'),
        ('ML_PREDICTIVE', 'Machine Learning Predictive'),
    ))

    macro_stability_index = models.DecimalField(max_digits=5, decimal_places=4)
    predictive_accuracy = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)

    forecast_payload = models.JSONField(default=dict)
    generated_at = models.DateTimeField(auto_now_add=True)

class StabilizationProtocol(BaseErpModel):
    """
    Capital Buffer Stabilization Protocol - Phase 24.5.
    Protocolos conjuntos Holding-Estado ante crisis de liquidez o volatilidad.
    """
    protocol_code = models.CharField(max_length=50, unique=True)
    trigger_event = models.CharField(max_length=255)

    activation_threshold = models.DecimalField(max_digits=5, decimal_places=4)
    action_plan = models.JSONField()

    is_legally_binding = models.BooleanField(default=True)
    last_activation_date = models.DateTimeField(null=True, blank=True)
