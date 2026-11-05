# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_contable/capitan_asientos_automaticos.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanAsientosAutomaticos(CapitanTemplate):
    """
    Agente de Asientos: Genera registros contables automáticos a partir de eventos de negocio.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Asientos): Generando registro para misión {mision.id}")

        pasos = {
            "generacion_asiento": {
                "descripcion": "Traducir evento de negocio a partida doble.",
                "teniente": "admin_persistencia_contable",
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
        from apps.sarita_agents.agents.general.sarita.coroneles.administrador_general.tenientes.operativos.tenientes_persistencia import AdminTenientePersistenciaContable
        return {
            "admin_persistencia_contable": AdminTenientePersistenciaContable()
        }
