# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/capitan_incidentes_operativos.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanIncidentesOperativos(CapitanTemplate):
    """
    Agente de Incidencias: Registra y gestiona fallos en la prestación del servicio.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Incidencias): Gestionando reporte para misión {mision.id}")

        pasos = {
            "registro_falla": {
                "descripcion": "Documentar la incidencia y notificar a los responsables.",
                "teniente": "gestor_fallas_operativas",
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
        class TenienteGestorFallas:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Incidencia registrada y escalada exitosamente."}

        return {
            "gestor_fallas_operativas": TenienteGestorFallas()
        }
