import logging
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel

logger = logging.getLogger(__name__)

class AntifragileSystem:
    """
    Motor Antifrágil (Fase 5).
    Reacciona a crisis sistémicas para proteger la integridad del holding.
    """

    def __init__(self, user):
        self.kernel = GovernanceKernel(user=user)

    def trigger_defensive_mode(self, reason, impact_severity="HIGH"):
        """
        Activa el Modo Defensivo del sistema.
        """
        logger.critical(f"ANTIFRÁGIL: Activando MODO DEFENSIVO por {reason}")

        # 1. Transición de estado sistémico vía Kernel (Soberano)
        self.kernel.transition_systemic_state(
            new_level='CONTAINMENT',
            reason=f"ANTIFRAGILE_DEFENSE: {reason}",
            context={"severity": impact_severity}
        )

        # 2. Acciones automáticas de protección de caja
        # - Bloquear gastos no críticos
        # - Activar protocolos de retención masiva

        return {
            "status": "DEFENSIVE_MODE_ACTIVE",
            "protections": [
                "REDUCED_ADQUISITION_SPEND",
                "INTENSIVE_RETENTION_ACTIVE",
                "CONSERVATIVE_FORECASTING"
            ]
        }
