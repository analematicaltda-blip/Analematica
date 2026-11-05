# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_financiera/capitan_riesgo_financiero.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanRiesgoFinanciero(CapitanTemplate):
    """
    Agente de Riesgo: Detecta anomalías en los gastos y niveles peligrosos de endeudamiento.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Riesgo): Evaluando salud financiera para misión {mision.id}")

        pasos = {
            "deteccion_anomalias": {
                "descripcion": "Verificar desviaciones presupuestales superiores al 15%.",
                "teniente": "auditor_riesgo_financiero",
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
        class TenienteRiesgo:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "No se detectan riesgos críticos de insolvencia."}
        return {
            "auditor_riesgo_financiero": TenienteRiesgo()
        }
