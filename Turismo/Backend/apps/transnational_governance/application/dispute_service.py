import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from ..models import DisputeCase, GovernanceBody

logger = logging.getLogger(__name__)

class DisputeResolutionService:
    """
    Cross-Border Dispute Resolution Mechanism - Phase 22.5.
    Gestiona arbitraje internacional y paneles técnicos especializados.
    """

    @staticmethod
    @transaction.atomic
    def open_dispute(title, case_type, body_id, details):
        """
        Abre un nuevo caso de disputa transnacional.
        """
        body = GovernanceBody.objects.get(id=body_id)
        case = DisputeCase.objects.create(
            title=title,
            case_type=case_type,
            governance_body=body,
            resolution_details=details
        )

        logger.warning(f"Dispute Resolution: NEW CASE OPENED: {title}. Assigned to {body.name}")

        # Notify Strategic Council if high level
        if body.governance_level == 3:
            DisputeResolutionService._escalate_to_strategic_council(case)

        return case

    @staticmethod
    def _escalate_to_strategic_council(case):
        """
        Escala disputas críticas al Transnational Strategic Council (TSC).
        """
        case.status = 'ESCALATED'
        case.save()
        logger.error(f"Dispute Resolution: CASE ESCALATED to TSC: {case.title}")

    @staticmethod
    @transaction.atomic
    def resolve_case(case_id, resolution_text):
        """
        Cierra una disputa aplicando la resolución técnica o arbitral.
        """
        case = DisputeCase.objects.get(id=case_id)
        case.status = 'RESOLVED'
        case.resolution_details += f"\n\nFINAL RESOLUTION ({timezone.now()}): {resolution_text}"
        case.save()

        logger.info(f"Dispute Resolution: CASE RESOLVED: {case.title}")
        return True

class GovernanceOrchestrator:
    """
    Orquestador de Gobernanza Multinivel (Fase 22.6).
    Coordina la transición entre niveles Operacional, Regulatorio y Estratégico.
    """

    @staticmethod
    def process_governance_event(event_type, payload):
        """
        Determina qué nivel de gobernanza debe intervenir según la severidad del evento.
        """
        severity = payload.get('severity', 'LOW')

        if severity == 'CRITICAL':
            # Level 3: Strategic (TSC)
            logger.error("Governance: ESCALATING TO STRATEGIC LEVEL (TSC)")
            # Trigger TSC Session
        elif severity == 'MEDIUM':
            # Level 2: Regulatory (MRB/AOA)
            logger.warning("Governance: ACTIVATING REGULATORY OVERSIGHT (MRB/AOA)")
        else:
            # Level 1: Operational (Autonomous)
            logger.info("Governance: Event handled at OPERATIONAL LEVEL (Algorithmic)")

        return severity
