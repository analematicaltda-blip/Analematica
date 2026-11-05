import logging
from django.db import transaction
from ..models import OptimizationProposal, OptimizationAuditLog
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel

logger = logging.getLogger(__name__)

class GovernanceOptimizer:
    """
    Controlador de Gobernanza para Optimización: Ejecuta y revierte cambios sistémicos.
    """

    def __init__(self, user):
        self.user = user
        self.kernel = GovernanceKernel(user=user)

    def approve_optimization(self, proposal_id: str, justification: str):
        """Aprueba una propuesta de optimización."""
        with transaction.atomic():
            proposal = OptimizationProposal.objects.get(id=proposal_id)
            proposal.status = OptimizationProposal.Status.APPROVED
            proposal.decidida_por = self.user
            proposal.justificacion_admin = justification
            proposal.save()

            OptimizationAuditLog.objects.create(
                proposal=proposal,
                accion='APPROVE',
                usuario=self.user,
                detalles={'justification': justification}
            )

    def execute_optimization(self, proposal_id: str):
        """
        Ejecuta físicamente el ajuste en el sistema.
        En Phase 6, esto simula el cambio de parámetros en el kernel/agentes.
        """
        proposal = OptimizationProposal.objects.get(id=proposal_id)
        if proposal.status != OptimizationProposal.Status.APPROVED:
            raise ValueError("Solo se pueden ejecutar optimizaciones aprobadas.")

        with transaction.atomic():
            # Aquí se aplicarían los parámetros_cambio al motor real
            # Por ahora, registramos la ejecución en el Kernel
            self.kernel._log_audit(
                intention=type('Intention', (), {'name': 'SYSTEM_OPTIMIZATION'})(),
                parameters=proposal.parametros_cambio,
                result={'status': 'APPLIED'},
                is_sovereign=True
            )

            proposal.status = OptimizationProposal.Status.EXECUTED
            proposal.save()

            OptimizationAuditLog.objects.create(
                proposal=proposal,
                accion='EXECUTE',
                usuario=self.user,
                detalles=proposal.parametros_cambio
            )
            logger.info(f"OPTIMIZATION: Ejecutada mejora {proposal.id} en dominio {proposal.domain}")

    def rollback_optimization(self, proposal_id: str):
        """Revierte una optimización a su estado previo."""
        proposal = OptimizationProposal.objects.get(id=proposal_id)
        if proposal.status != OptimizationProposal.Status.EXECUTED:
            raise ValueError("Solo se pueden revertir optimizaciones ya ejecutadas.")

        with transaction.atomic():
            # Restauramos config_previa
            # (Lógica de restauración aquí)

            proposal.status = OptimizationProposal.Status.REVERTED
            proposal.save()

            OptimizationAuditLog.objects.create(
                proposal=proposal,
                accion='ROLLBACK',
                usuario=self.user,
                detalles={'reverted_to': proposal.config_previa}
            )
            logger.warning(f"OPTIMIZATION: Revertida mejora {proposal.id}")
