import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from .capitan_interop import CapitanInteroperabilidad

logger = logging.getLogger(__name__)

class CoronelInteroperabilidad(CoronelTemplate):
    """
    Coronel de Interoperabilidad: Responsable de la infraestructura sistémica que une los silos.
    """
    def __init__(self, general):
        super().__init__(general, domain="interop")

    def _get_capitanes(self) -> dict:
        return {
            "interop_general": CapitanInteroperabilidad(self)
        }

    def _select_capitan(self, mission: dict):
        # Por ahora solo tenemos uno general
        return self.capitanes["interop_general"]
