import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import MetaEcosystem, EcosystemInterdependence, GlobalUtilityMetric

logger = logging.getLogger(__name__)

class CEOEService:
    """
    Cross-Ecosystem Orchestration Engine (CEOE) - Phase 20.5.
    Coordina flujos inter-ecosistema y maximiza la Utilidad Global.
    """

    @staticmethod
    @transaction.atomic
    def run_meta_orchestration():
        """
        Ciclo central de orquestación supra-corporativa.
        Calcula interdependencias y ajusta parámetros macro.
        """
        ecosystems = MetaEcosystem.objects.filter(is_active=True)
        global_utility_aggregate = Decimal('0')

        for eco in ecosystems:
            # 1. Update interdependence score based on dependencies
            CEOEService._update_interdependence_metrics(eco)

            # 2. Calculate Global Utility contribution
            utility = CEOEService.calculate_global_utility(eco)
            global_utility_aggregate += utility.net_global_utility

        logger.info(f"CEOE: Meta-Orchestration Cycle Complete. Aggregate Global Utility: {global_utility_aggregate}")
        return {
            "aggregate_global_utility": global_utility_aggregate,
            "ecosystem_count": ecosystems.count()
        }

    @staticmethod
    def calculate_global_utility(ecosystem):
        """
        Modelo Matemático Meta-Económico (Fase 20.5).
        GlobalUtility = Contribution - Externality - SystemicRisk
        """
        # Simplificación de métricas para el motor
        contribution = ecosystem.economic_output * Decimal('0.1') # Contribution score
        externality = ecosystem.regulatory_exposure * Decimal('1000000') # Cost of externalities
        risk_penalty = ecosystem.risk_index * ecosystem.interdependence_score * Decimal('5000000')

        net_utility = contribution - externality - risk_penalty

        # Save historical record
        metric = GlobalUtilityMetric.objects.create(
            ecosystem=ecosystem,
            period=timezone.now().strftime("%Y-%m"),
            contribution_score=contribution,
            externality_cost=externality,
            risk_penalty=risk_penalty,
            net_global_utility=net_utility
        )

        return metric

    @staticmethod
    def _update_interdependence_metrics(ecosystem):
        """
        Calcula el índice de interdependencia basado en el peso de las conexiones.
        """
        dependencies = ecosystem.outgoing_dependencies.all()
        if dependencies:
            total_weight = sum(d.dependency_weight for d in dependencies)
            ecosystem.interdependence_score = Decimal(str(min(total_weight / Decimal('5.0'), 1.0)))
        else:
            ecosystem.interdependence_score = Decimal('0.1')

        ecosystem.save()

    @staticmethod
    @transaction.atomic
    def synchronize_inter_ecosystem_liquidity(source_id, target_id, amount):
        """
        Sincroniza liquidez entre dos ecosistemas para balancear riesgos compartidos.
        """
        source = MetaEcosystem.objects.get(id=source_id)
        target = MetaEcosystem.objects.get(id=target_id)

        if source.liquidity_depth >= amount:
            source.liquidity_depth -= amount
            target.liquidity_depth += amount
            source.save()
            target.save()

            logger.info(f"CEOE: Synchronized {amount} liquidity from {source.name} to {target.name}")
            return True
        return False
