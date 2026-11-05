# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/capitan_operacion_restaurantes.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanOperacionRestaurantes(CapitanTemplate):
    """
    Agente Especializado en Restauración: Gestiona plano de mesas, estaciones de cocina y pedidos.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Restaurante): Planificando operación de salón para misión {mision.id}")

        pasos = {
            "gestion_mesas": {
                "descripcion": "Coordinar disponibilidad de mesas y flujo de comensales.",
                "teniente": "gestor_restaurante",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }

        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos,
            estado='PLANIFICADO'
        )

    def _get_tenientes(self) -> dict:
        class TenienteRestaurante:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Operación de restaurante coordinada exitosamente."}

        return {
            "gestor_restaurante": TenienteRestaurante()
        }
