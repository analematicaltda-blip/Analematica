# backend/apps/sarita_agents/finanzas/capitan_roi.py
import logging
from ..agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanROI(CapitanTemplate):
    """
    Capitán ROI: Evalúa la rentabilidad y decide si escalar o frenar.
    """
    def _get_tenientes(self) -> dict:
        return {
            "calculator": "roi_calculator"
        }

    def plan(self, mision: Mision) -> PlanTáctico:
        params = mision.directiva_original.get("parameters", {})

        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan={
                "1": {
                    "teniente": self.tenientes["calculator"],
                    "descripcion": "Calcular ROI estratégico",
                    "parametros": params
                }
            }
        )

    def evaluate_roi(self, cac, ltv):
        if cac == 0: return 100.0
        roi = (ltv - cac) / cac
        return roi
