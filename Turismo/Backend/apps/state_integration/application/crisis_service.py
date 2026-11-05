import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import InfrastructureProject, StateEntity

logger = logging.getLogger(__name__)

class CrisisCoordinationService:
    """
    Crisis Coordination Protocol - Phase 21.5.
    Coordina liquidez y apoyo logístico a infraestructuras críticas nacionales durante emergencias.
    """

    @staticmethod
    @transaction.atomic
    def mobilize_crisis_liquidity(project_id, amount, reason="Financial Crisis"):
        """
        Moviliza buffers financieros para apoyar proyectos de infraestructura estratégica nacional.
        """
        project = InfrastructureProject.objects.get(id=project_id)
        if project.status == 'ACTIVE':
            # 1. Mobilize capital from holding treasury
            # Integration with strategic_treasury (Phase 13)
            project.capital_committed += amount
            project.save()

            logger.warning(f"Crisis Coordination: Mobilized {amount} for {project.name}. Reason: {reason}")

            # 2. Trigger notification to SIPL Gateway
            from .interop_service import InteroperabilityService
            InteroperabilityService.synchronize_state_financials(
                project.lead_state_entity.id,
                amount,
                "COP"
            )

            # Notify Control Tower (Phase C)
            from apps.control_tower.application.anomaly_service import AnomalyService
            AnomalyService.detect_anomaly(
                metric="state_crisis_support",
                value=float(amount),
                threshold=0.0,
                severity="HIGH",
                description=f"Emergency capital mobilization for national infrastructure {project.name}"
            )

            return True
        return False

    @staticmethod
    def coordinate_logistics_support(project_id, resources_payload):
        """
        Coordina apoyo operativo a redes logísticas estatales críticas.
        """
        project = InfrastructureProject.objects.get(id=project_id)
        # Simulation: Logistical support active
        logger.info(f"Crisis Coordination: OPERATIONAL SUPPORT ACTIVE for {project.name} [{project.project_type}]")

        return True
