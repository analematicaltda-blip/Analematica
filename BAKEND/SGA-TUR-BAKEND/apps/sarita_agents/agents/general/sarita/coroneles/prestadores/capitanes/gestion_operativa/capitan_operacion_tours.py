# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/capitan_operacion_tours.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanOperacionTours(CapitanTemplate):
    """
    Agente Especializado en Tours: Gestiona itinerarios, guías y experiencias turísticas.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Tours): Planificando experiencia para misión {mision.id}")

        pasos = {
            "gestion_experiencia": {
                "descripcion": "Asignar guía calificado y preparar logística del itinerario.",
                "teniente": "gestor_tours",
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
        class TenienteTours:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Itinerario de tour validado y activo."}

        return {
            "gestor_tours": TenienteTours()
        }
