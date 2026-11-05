from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico
import logging

logger = logging.getLogger(__name__)

class AdminCapitanOperativo(CapitanTemplate):
    """
    Capitán Operativo para el ERP del Super Admin.
    Replica el flujo operativo para la gestión de recursos de la plataforma.
    """
    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"ADMIN CAPITÁN (Operativo): Planificando gestión en admin_operativa.")
        pasos = {
            "gestion_recursos": {
                "descripcion": "Ejecutar acción operativa sobre los recursos de la plataforma.",
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
        return {}
