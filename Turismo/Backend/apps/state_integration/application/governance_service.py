import logging
from decimal import Decimal
from django.db import transaction
from ..models import JointGovernanceCommittee, InfrastructureProject, StateEntity

logger = logging.getLogger(__name__)

class JointGovernanceService:
    """
    Joint Governance Interface (JGI) - Phase 21.5.
    Gestiona la gobernanza compartida Holding-Estado y protocolos de intervención.
    """

    @staticmethod
    def register_joint_committee(state_entity_id, members_list, scope):
        """
        Establece un comité mixto para supervisión de proyectos críticos.
        """
        entity = StateEntity.objects.get(id=state_entity_id)
        committee = JointGovernanceCommittee.objects.create(
            name=f"Joint Committee {entity.name}",
            state_entity=entity,
            committee_members=members_list,
            oversight_scope=scope,
            intervention_protocol=entity.integration_config.get('intervention_protocol', {})
        )

        logger.info(f"JGI: Joint Committee established for {entity.name}")
        return committee

    @staticmethod
    @transaction.atomic
    def activate_state_intervention(committee_id):
        """
        Activa el protocolo de intervención estatal bajo cláusulas contractuales predefinidas.
        Garantiza estabilidad institucional ante crisis extremas.
        """
        committee = JointGovernanceCommittee.objects.get(id=committee_id)
        if committee.is_active:
            # 1. Trigger protocol from integration_config
            protocol = committee.intervention_protocol

            # Simulation: State supervision active
            logger.warning(f"JGI: STATE INTERVENTION ACTIVE for {committee.name}. Scope: {committee.oversight_scope}")

            # Integration with EnterprisePolicy (Phase 8)
            # from apps.enterprise.application.policy_service import PolicyService
            # PolicyService.activate_sovereign_override(committee_id)

            return True
        return False
