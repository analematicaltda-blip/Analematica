import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import SystemicRiskIndicator, MacroCouncil

logger = logging.getLogger(__name__)

class SystemicRiskService:
    """
    Systemic Risk Observatory (SRO) - Phase 24.2.
    Monitorea estabilidad macro y calcula el riesgo de contagio sistémico.
    """

    @staticmethod
    @transaction.atomic
    def analyze_systemic_risk(council_id):
        """
        Calcula el Riesgo Sistémico Agregado.
        SR = f(LiquidityShock, CapitalVolatility, Interconnectedness, Leverage)
        """
        council = MacroCouncil.objects.get(id=council_id)

        # Simulation: Aggregate data from multiple economic nodes
        liq_shock = Decimal('0.15')
        cap_volat = Decimal('0.22')
        intercon = Decimal('0.65') # Highly interconnected
        lev_ratio = Decimal('0.40')

        # Formula: Weighted average risk
        net_risk = (
            (liq_shock * Decimal('0.30')) +
            (cap_volat * Decimal('0.25')) +
            (intercon * Decimal('0.30')) +
            (lev_ratio * Decimal('0.15'))
        ).quantize(Decimal('0.0001'))

        indicator = SystemicRiskIndicator.objects.create(
            council=council,
            indicator_name=f"Aggregated Macro Risk {timezone.now().date()}",
            liquidity_shock_factor=liq_shock,
            capital_volatility_index=cap_volat,
            interconnectedness_score=intercon,
            leverage_ratio=lev_ratio,
            net_systemic_risk=net_risk
        )

        logger.info(f"SRO: Systemic Risk calculated for {council.name}: {net_risk}")

        if net_risk > Decimal('0.75'):
            # Trigger Strategic Escalation (Level 3 Coordination)
            SystemicRiskService._escalate_macro_crisis(council)

        return indicator

    @staticmethod
    def _escalate_macro_crisis(council):
        """
        Escala la coordinación a Nivel 3 ante riesgo sistémico crítico.
        """
        council.coordination_level = 3
        council.save()
        logger.error(f"SRO: MACRO CRISIS DETECTED. Coordination Level for {council.name} set to STRATEGIC.")

        # Integration with stabilization protocols (Phase 24.5)
        # from .coordination_engine import CoordinationEngineService
        # CoordinationEngineService.activate_all_private_buffers()
