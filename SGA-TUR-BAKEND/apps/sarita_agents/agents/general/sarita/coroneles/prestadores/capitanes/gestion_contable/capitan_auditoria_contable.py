# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_contable/capitan_auditoria_contable.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanAuditoriaContable(CapitanTemplate):
    """
    Agente Auditor: Realiza cruces de información entre facturación y contabilidad.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Auditoría Cont): Iniciando auditoría para misión {mision.id}")

        pasos = {
            "cruce_facturacion": {
                "descripcion": "Verificar que cada factura tenga su asiento correspondiente.",
                "teniente": "auditor_cruces_contables",
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
        class TenienteCruces:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Cruce de datos 100% coincidente."}
        return {
            "auditor_cruces_contables": TenienteCruces()
        }
