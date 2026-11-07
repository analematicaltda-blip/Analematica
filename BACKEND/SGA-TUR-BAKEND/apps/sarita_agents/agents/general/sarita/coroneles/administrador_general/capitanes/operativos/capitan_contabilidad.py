from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico
import logging

logger = logging.getLogger(__name__)

class AdminCapitanContabilidad(CapitanTemplate):
    """
    Capitán Operativo para el ERP del Super Admin.
    Replica el flujo contable para la gestión de la plataforma.
    """
    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"ADMIN CAPITÁN (Contable): Planificando registro en admin_contabilidad.")
        pasos = {
            "registro_asiento": {
                "descripcion": "Generar asiento contable en el ERP administrativo.",
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
        return {}
