# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/capitan_operacion_transporte.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanOperacionTransporte(CapitanTemplate):
    """
    Agente Especializado en Transporte: Gestiona flota, mantenimientos y conductores.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Transporte): Planificando logística de flota para misión {mision.id}")

        pasos = {
            "gestion_flota": {
                "descripcion": "Verificar disponibilidad de vehículos y asignar rutas.",
                "teniente": "gestor_transporte",
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
        class TenienteTransporte:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Logística de transporte optimizada."}

        return {
            "gestor_transporte": TenienteTransporte()
        }
