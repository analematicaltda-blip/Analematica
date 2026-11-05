import logging
from django.utils import timezone
from apps.decision_intelligence.models import StrategyProposal
from ..models import PerformanceMetric

logger = logging.getLogger(__name__)

class PerformanceTracker:
    """
    Capa de Evaluación Continua: Mide la efectividad de los agentes y la confianza del Super Admin.
    """

    def record_decision_outcome(self, proposal: StrategyProposal):
        """
        Registra el resultado de una decisión estratégica para análisis futuro.
        """
        # 1. Registrar Aceptación (Confianza)
        is_accepted = proposal.status in [StrategyProposal.Status.APPROVED, StrategyProposal.Status.EXECUTED]

        PerformanceMetric.objects.create(
            domain=PerformanceMetric.Domain.GOBERNANZA,
            metric_name='TRUST_LEVEL',
            value=1.0 if is_accepted else 0.0,
            metadata={
                'proposal_id': str(proposal.id),
                'agent_id': proposal.agent_id,
                'domain': proposal.domain,
                'status': proposal.status,
                'decision_level': proposal.decision_level
            }
        )

        # 2. Registrar éxito de ejecución
        if proposal.status == StrategyProposal.Status.EXECUTED:
            PerformanceMetric.objects.create(
                domain=proposal.domain,
                metric_name='EXECUTION_SUCCESS',
                value=1.0,
                metadata={'proposal_id': str(proposal.id)}
            )
        elif proposal.status == StrategyProposal.Status.FAILED:
            PerformanceMetric.objects.create(
                domain=proposal.domain,
                metric_name='EXECUTION_SUCCESS',
                value=0.0,
                metadata={'proposal_id': str(proposal.id)}
            )

    def get_super_admin_trust_index(self, domain=None) -> float:
        """
        Calcula el índice de confianza basado en la tasa de aceptación histórica.
        """
        query = PerformanceMetric.objects.filter(metric_name='TRUST_LEVEL')
        if domain:
            # Filtramos por las propuestas que pertenecen al dominio,
            # asumiendo que el metadato lo tiene.
            query = query.filter(metadata__domain=domain)

        count = query.count()
        if count == 0:
            return 1.0 # Confianza total inicial

        accepted = query.filter(value=1.0).count()
        return accepted / count

    def get_noise_level(self, domain: str) -> float:
        """
        Mide el nivel de 'ruido' (propuestas rechazadas) en un dominio específico.
        """
        trust = self.get_super_admin_trust_index(domain)
        return 1.0 - trust
