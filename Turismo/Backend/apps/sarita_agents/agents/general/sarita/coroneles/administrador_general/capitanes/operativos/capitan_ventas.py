from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico
import logging

logger = logging.getLogger(__name__)

class AdminCapitanVentas(CapitanTemplate):
    """
    Capitán Operativo para el ERP del Super Admin.
    Replica el flujo de ventas para la gestión de Planes y Suscripciones.
    """
    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"ADMIN CAPITÁN (Ventas): Planificando operación en dominio admin_comercial.")
        # Replicación funcional del flujo de cierre de ventas de planes
        pasos = {
            "registro_operacion": {
                "descripcion": "Registrar nueva intención de venta de plan en admin_comercial.",
                "teniente": "admin_persistencia_comercial",
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
        return {} # Se registrarán en el mapa global
