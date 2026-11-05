from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico
import logging

logger = logging.getLogger(__name__)

class AdminCapitanFinanciero(CapitanTemplate):
    """
    Capitán Operativo para el ERP del Super Admin.
    Replica el flujo financiero para la gestión de ingresos de plataforma.
    """
    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"ADMIN CAPITÁN (Financiero): Planificando movimiento en admin_financiera.")
        pasos = {
            "registro_pago": {
                "descripcion": "Registrar ingreso financiero en cuentas administrativas.",
                "teniente": "admin_persistencia_financiera",
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
