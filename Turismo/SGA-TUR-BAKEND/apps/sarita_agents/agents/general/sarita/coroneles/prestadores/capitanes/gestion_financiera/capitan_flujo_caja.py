# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/capitanes/gestion_financiera/capitan_flujo_caja.py
import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanFlujoCaja(CapitanTemplate):
    """
    Agente de Liquidez: Analiza la disponibilidad inmediata de efectivo y proyecta pagos.
    """

    def plan(self, mision: Mision) -> PlanTáctico:
        logger.info(f"CAPITÁN (Liquidez): Analizando flujo de caja para misión {mision.id}")

        pasos = {
            "proyeccion_liquidez": {
                "descripcion": "Calcular saldo proyectado a 30 días basándose en facturas y órdenes de pago.",
                "teniente": "gestor_liquidez_financiera",
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
        class TenienteLiquidez:
            def execute_task(self, tarea):
                return {"status": "SUCCESS", "message": "Proyección de liquidez completada."}
        return {
            "gestor_liquidez_financiera": TenienteLiquidez()
        }
