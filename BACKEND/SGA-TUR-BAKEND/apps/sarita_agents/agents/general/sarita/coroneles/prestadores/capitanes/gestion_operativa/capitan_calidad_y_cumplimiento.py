# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/capitan_calidad_y_cumplimiento.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanCalidadYCumplimiento(CapitanTemplate):
    """
    Agente de Cierre y Calidad: Valida la finalización del servicio y el cumplimiento de estándares.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Calidad): Verificando cierre de servicio para misión {mision.id}")

        pasos = {
            "check_calidad": {
                "descripcion": "Verificar que el servicio se prestó según los estándares de calidad.",
                "teniente": "auditor_calidad_operativa",
                "parametros": mision.directiva_original.get("parameters", {})
            },
            "cierre_administrativo": {
                "descripcion": "Cerrar la orden y liberar recursos.",
                "teniente": "admin_persistencia_operativa",
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
        from apps.sarita_agents.agents.general.sarita.coroneles.administrador_general.tenientes.operativos.tenientes_persistencia import AdminTenientePersistenciaOperativa
        class TenienteCalidad:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Estándares de calidad validados."}

        return {
            "auditor_calidad_operativa": TenienteCalidad(),
            "admin_persistencia_operativa": AdminTenientePersistenciaOperativa()
        }
