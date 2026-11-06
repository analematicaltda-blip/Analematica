# backend/apps/sarita_agents/finanzas/capitan_ltv.py
import logging
from ..agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanLTV(CapitanTemplate):
    """
    Capitán LTV: Proyecta el Valor de Vida del Cliente.
    """
    def _get_tenientes(self) -> dict:
        return {
            "calculator": "ltv_calculator"
        }

    def plan(self, mision: Mision) -> PlanTáctico:
        params = mision.directiva_original.get("parameters", {})

        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan={
                "1": {
                    "teniente": self.tenientes["calculator"],
                    "descripcion": "Proyectar LTV",
                    "parametros": params
                }
            }
        )

    def estimate_ltv(self, user_type, plan_value):
        # LTV = plan_mensual * meses_retencion * factor_upsell
        meses_retencion = 12 if user_type == 'gobierno' else 6
        factor_upsell = 1.2

        return plan_value * meses_retencion * factor_upsell
