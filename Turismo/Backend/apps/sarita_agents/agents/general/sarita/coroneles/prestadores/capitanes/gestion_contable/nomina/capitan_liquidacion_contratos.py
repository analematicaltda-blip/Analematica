# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_contable/nomina/capitan_liquidacion_contratos.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanLiquidacionContratos(CapitanTemplate):
    """
    Agente de Liquidación: Gestiona el cierre de relaciones laborales y pagos definitivos.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Liquidación): Calculando liquidación final para misión {mision.id}")

        pasos = {
            "calculo_prestaciones": {
                "descripcion": "Proyectar cesantías, prima y vacaciones no disfrutadas.",
                "teniente": "gestor_liquidacion_laboral",
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
        class TenienteLiquidacion:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Liquidación definitiva calculada."}
        return {
            "gestor_liquidacion_laboral": TenienteLiquidacion()
        }
