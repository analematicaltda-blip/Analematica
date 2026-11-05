import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import JurisdictionalNode, RegulatoryProfile, CapitalShield

logger = logging.getLogger(__name__)

class RegulatoryIntelligenceService:
    """
    Autonomous Regulatory Intelligence Engine (ARIE) - Phase 19.4.
    Analiza estabilidad legal, fiscal y geopolítica para optimizar la resiliencia sistémica.
    """

    @staticmethod
    def calculate_sovereign_resilience(node_id):
        """
        Modelo Matemático de Resiliencia Soberana (Fase 19.5).
        f(Diversification, Redundancy, Liquidity, LegalStability, TechIndependence)
        """
        node = JurisdictionalNode.objects.select_related('regulatory_profile').get(id=node_id)
        profile = node.regulatory_profile

        # 1. Diversification: Number of active sub-nodes (Regional/Operational)
        sub_nodes_count = node.sub_nodes.filter(is_active=True).count()
        diversification_score = Decimal(str(min(sub_nodes_count / 10.0, 1.0)))

        # 2. Redundancy: Multiple capital shields in different currencies/types
        shield_types = node.capital_shields.values_list('asset_type', flat=True).distinct().count()
        redundancy_score = Decimal(str(min(shield_types / 4.0, 1.0)))

        # 3. Liquidity: Weighted average liquidity_ratio of shields
        shields = node.capital_shields.all()
        if shields:
            liquidity_score = sum(s.liquidity_ratio for s in shields) / shields.count()
        else:
            liquidity_score = Decimal('0.0')

        # 4. Legal Stability: Stability Index - Political Risk
        stability_score = node.stability_index - node.political_risk_score

        # Final Resilience Index
        resilience_index = (
            (diversification_score * Decimal('0.25')) +
            (redundancy_score * Decimal('0.25')) +
            (liquidity_score * Decimal('0.20')) +
            (stability_score * Decimal('0.30'))
        ).quantize(Decimal('0.0001'))

        logger.info(f"ARIE: Resilience Index for {node.name}: {resilience_index}")
        return resilience_index

    @staticmethod
    @transaction.atomic
    def simulate_regulatory_impact(jurisdiction_code, shock_type='TAX_HIKE'):
        """
        Simula impacto normativo y rebalancea activos si la resiliencia cae bajo el umbral.
        """
        affected_nodes = JurisdictionalNode.objects.filter(country_code=jurisdiction_code)

        for node in affected_nodes:
            if shock_type == 'TAX_HIKE':
                # Costs increase, stability drops
                node.stability_index -= Decimal('0.15')
            elif shock_type == 'CAPITAL_CONTROL':
                # Liquidity is compromised
                node.regulatory_profile.capital_controls = True
                node.capital_shields.update(liquidity_ratio=Decimal('0.20'))

            node.save()
            node.regulatory_profile.save()

            resilience = RegulatoryIntelligenceService.calculate_sovereign_resilience(node.id)

            if resilience < node.regulatory_profile.alert_threshold:
                # Trigger Sovereign Migration (Fase 19.6)
                RegulatoryIntelligenceService.rebalance_assets(node.id)

        return affected_nodes.count()

    @staticmethod
    @transaction.atomic
    def rebalance_assets(compromised_node_id):
        """
        Migra capital de un nodo vulnerable a un nodo estable (ROOT o Regional seguro).
        """
        source = JurisdictionalNode.objects.get(id=compromised_node_id)

        # Find safest regional target
        target = JurisdictionalNode.objects.filter(
            level='REGIONAL',
            is_active=True,
            stability_index__gt=Decimal('0.8')
        ).order_by('-stability_index').first()

        if not target:
            # Fallback to ROOT
            target = JurisdictionalNode.objects.filter(level='ROOT', is_active=True).first()

        if target and target.id != source.id:
            for shield in source.capital_shields.filter(is_locked=False):
                # Transfer 80% of value to target (Migration)
                migration_amount = shield.current_value * Decimal('0.8')

                target_shield, created = CapitalShield.objects.get_or_create(
                    node=target,
                    asset_type=shield.asset_type,
                    currency=shield.currency,
                    defaults={'current_value': Decimal('0')}
                )

                target_shield.current_value += migration_amount
                target_shield.save()

                shield.current_value -= migration_amount
                shield.save()

                logger.warning(f"ARIE: MIGRATED {migration_amount} {shield.currency} from {source.name} to {target.name}")

            return True
        return False
