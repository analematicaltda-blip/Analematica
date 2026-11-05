# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_operativa/sg_sst/capitan_incidentes_sst.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanIncidentesSST(CapitanTemplate):
    """
    Agente de Incidentes SST: Gestiona el rastro de accidentes y casi-accidentes laborales.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Incidencias SST): Documentando evento para misión {mision.id}")

        pasos = {
            "registro_incidente": {
                "descripcion": "Crear registro de incidente y disparar flujo de investigación.",
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
