import logging
from apps.sarita_agents.agents.soldado_template import SoldadoN6
from apps.enterprise_core.integration.governance_adapter import GovernanceAdapter

logger = logging.getLogger(__name__)

class StrategicExecutionAgent(SoldadoN6):
    """
    Fase 9: Soldado N6 - Brazo Ejecutor de Decisiones IA.
    Capaz de modificar parámetros de negocio (precios, stock, campañas)
    siempre bajo la validación del GovernanceKernel.
    """

    def execute(self, micro_tarea_id: str):
        micro_tarea = self._get_micro_tarea(micro_tarea_id)
        params = micro_tarea.parametros
        intention = params.get("intention")

        logger.info(f"StrategicExecutionAgent: Ejecutando intención estratégica: {intention}")

        try:
            # 1. Validar y ejecutar vía Adaptador de Gobernanza
            # El agente no tiene 'user', por lo que el kernel debe identificar la firma del agente
            result = GovernanceAdapter.validate_and_execute(
                intention=intention,
                parameters=params.get("payload", {}),
                user=None
            )

            if result.get("status") == "SUCCESS":
                self._registrar_exito(micro_tarea_id, result)
            else:
                self._registrar_fallo(micro_tarea_id, f"Governance Rejection: {result.get('error')}")

        except Exception as e:
            logger.error(f"StrategicExecutionAgent: Error crítico en ejecución: {e}")
            self._registrar_fallo(micro_tarea_id, str(e))
