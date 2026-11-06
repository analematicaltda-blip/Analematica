import logging
from decimal import Decimal
from django.db import transaction
from ..models import MetaEcosystem, EcosystemInterdependence

logger = logging.getLogger(__name__)

class MetaRiskService:
    """
    Distributed Risk Containment - Phase 20.5.
    Implementa firewalls económicos y protocolos de aislamiento inter-ecosistema.
    """

    @staticmethod
    @transaction.atomic
    def analyze_cross_ecosystem_contagion():
        """
        Detecta si un fallo en un ecosistema está amenazando la estabilidad de la red meta-económica.
        """
        ecosystems = MetaEcosystem.objects.filter(is_active=True)
        firewalls_activated = 0

        for eco in ecosystems:
            if eco.risk_index > Decimal('0.8'):
                # Critical risk node detected -> Trigger Meta-Isolation
                MetaRiskService.activate_economic_firewall(eco.id)
                firewalls_activated += 1

        return firewalls_activated

    @staticmethod
    @transaction.atomic
    def activate_economic_firewall(ecosystem_id):
        """
        Aísla un ecosistema limitando sus interdependencias entrantes y salientes (Firewall).
        """
        ecosystem = MetaEcosystem.objects.get(id=ecosystem_id)
        ecosystem.status = 'FIREWALL_ACTIVE' # Hypothetical status
        ecosystem.is_active = False
        ecosystem.save()

        # Neutralize weight of all interdependences involving this node
        EcosystemInterdependence.objects.filter(source_ecosystem=ecosystem).update(dependency_weight=Decimal('0'))
        EcosystemInterdependence.objects.filter(target_ecosystem=ecosystem).update(dependency_weight=Decimal('0'))

        logger.error(f"Meta-Risk: FIREWALL ACTIVATED for {ecosystem.name}. Systemic Contagion Blocked.")

        # Notify Control Tower (Phase C)
        from apps.control_tower.application.anomaly_service import AnomalyService
        AnomalyService.detect_anomaly(
            metric="meta_ecosystem_risk",
            value=float(ecosystem.risk_index),
            threshold=0.8,
            severity="CRITICAL",
            description=f"Economic Firewall activated for {ecosystem.name} to prevent meta-network contagion"
        )

        return True
