# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_archivistica/capitan_archivistico.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanArchivistico(CapitanTemplate):
    """
    Agente Archivístico: Gestiona la organización y el ciclo de vida de los documentos.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Archivístico): Planificando gestión documental para misión {mision.id}")

        pasos = {
            "organizacion_documental": {
                "descripcion": "Clasificar y organizar documentos en el expediente digital.",
                "teniente": "admin_persistencia_archivistica",
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
        return {
            "admin_persistencia_archivistica": "admin_persistencia_archivistica"
        }
