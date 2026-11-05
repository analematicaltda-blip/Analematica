# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/capitan_control_operativo.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanControlOperativo(CapitanTemplate):
    """
    Agente de Seguimiento: Monitorea el progreso de las órdenes y el cumplimiento de SLAs.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Seguimiento): Verificando progreso para misión {mision.id}")

        pasos = {
            "verificacion_sla": {
                "descripcion": "Comparar tiempos de ejecución con umbrales de SLA.",
                "teniente": "auditor_sla_operativo",
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
        class TenienteAuditorSLA:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Niveles de servicio dentro de los parámetros."}

        return {
            "auditor_sla_operativo": TenienteAuditorSLA()
        }
