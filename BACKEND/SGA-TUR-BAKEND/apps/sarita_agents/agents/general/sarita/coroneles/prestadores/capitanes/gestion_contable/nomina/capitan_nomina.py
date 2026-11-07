# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_contable/nomina/capitan_nomina.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanNomina(CapitanTemplate):
    """
    Agente de Nómina: Orquesta la generación de planillas y el pago a colaboradores.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Nómina): Planificando liquidación de periodo para misión {mision.id}")

        pasos = {
            "liquidacion_planilla": {
                "descripcion": "Calcular devengados y deducciones para todos los contratos activos.",
                "teniente": "nomina_liquidacion",
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
        from apps.sarita_agents.agents.general.sarita.coroneles.nomina.tenientes.tenientes_nomina import TenienteLiquidacion
        return {
            "nomina_liquidacion": TenienteLiquidacion()
        }
