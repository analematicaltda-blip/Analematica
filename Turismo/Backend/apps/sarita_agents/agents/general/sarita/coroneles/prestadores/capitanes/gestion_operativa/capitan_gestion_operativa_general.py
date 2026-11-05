# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/capitan_gestion_operativa_general.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanGestionOperativaGeneral(CapitanTemplate):
    """
    Agente Operativo General: Orquesta la ejecución de servicios y órdenes de trabajo.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Op General): Planificando ejecución para misión {mision.id}")

        pasos = {
            "creacion_orden": {
                "descripcion": "Generar orden de servicio en el dominio operativo.",
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
        return {
            "admin_persistencia_operativa": AdminTenientePersistenciaOperativa()
        }
