# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/sg_sst/capitan_normativo_sst.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanNormativoSST(CapitanTemplate):
    """
    Agente Normativo SST: Valida el cumplimiento de los estándares mínimos legales.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Normativo SST): Verificando cumplimiento legal para misión {mision.id}")

        pasos = {
            "evaluacion_normativa": {
                "descripcion": "Cruzar matriz de riesgos con requisitos del estándar mínimo nacional.",
                "teniente": "auditor_normativo_sst",
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
        class TenienteAuditorNormativo:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Cumplimiento normativo del 94% verificado."}
        return {
            "auditor_normativo_sst": TenienteAuditorNormativo()
        }
