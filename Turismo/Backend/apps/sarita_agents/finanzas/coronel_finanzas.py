# backend/apps/sarita_agents/finanzas/coronel_finanzas.py
import logging
from ..agents.coronel_template import CoronelTemplate
from .capitan_cac import CapitanCAC
from .capitan_ltv import CapitanLTV
from .capitan_roi import CapitanROI

logger = logging.getLogger(__name__)

class CoronelFinanzas(CoronelTemplate):
    """
    Coronel Financiero Estratégico: Supervisa métricas de adquisición y rentabilidad.
    """
    def _get_capitanes(self) -> dict:
        return {
            "cac": CapitanCAC(coronel=self),
            "ltv": CapitanLTV(coronel=self),
            "roi": CapitanROI(coronel=self)
        }

    def _select_capitan(self, mission: dict):
        mission_type = mission.get("mission", {}).get("type")
        if "CAC" in mission_type: return self.capitanes["cac"]
        if "LTV" in mission_type: return self.capitanes["ltv"]
        if "ROI" in mission_type: return self.capitanes["roi"]
        return self.capitanes["roi"] # Default to ROI analysis
