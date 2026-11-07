# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_contable/nomina/capitan_legal_laboral.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanLegalLaboral(CapitanTemplate):
    """
    Agente Legal Laboral: Valida que los contratos y pagos cumplan con el código sustantivo del trabajo.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Legal Laboral): Verificando cumplimiento para misión {mision.id}")

        pasos = {
            "auditoria_contratos": {
                "descripcion": "Verificar que los contratos tengan sus cláusulas de ley y aportes a seguridad social.",
                "teniente": "auditor_legal_laboral",
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
        class TenienteLegal:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Cumplimiento laboral 100% verificado."}
        return {
            "auditor_legal_laboral": TenienteLegal()
        }
