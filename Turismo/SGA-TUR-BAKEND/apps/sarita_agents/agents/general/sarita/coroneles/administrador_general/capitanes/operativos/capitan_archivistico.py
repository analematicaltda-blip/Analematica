from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico
import logging

logger = logging.getLogger(__name__)

class AdminCapitanArchivistico(CapitanTemplate):
    """
    Capitán Operativo para el ERP del Super Admin.
    Replica el flujo archivístico para la gestión documental de la plataforma.
    """
    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"ADMIN CAPITÁN (Archivístico): Planificando búsqueda/gestión en admin_archivistica.")
        pasos = {
            "gestion_documental": {
                "descripcion": "Ejecutar búsqueda o gestión sobre el archivo administrativo.",
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
        return {}
