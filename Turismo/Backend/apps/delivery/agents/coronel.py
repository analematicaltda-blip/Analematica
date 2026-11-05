import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from .capitanes import (
    CapitanDespacho,
    CapitanRutas,
    CapitanRepartidores,
    CapitanSeguimiento,
    CapitanIndicadores
)

logger = logging.getLogger(__name__)

class CoronelDelivery(CoronelTemplate):
    def __init__(self, general):
        super().__init__(general, domain="delivery")

    def _get_capitanes(self) -> dict:
        return {
            "despacho": CapitanDespacho(self),
            "rutas": CapitanRutas(self),
            "repartidores": CapitanRepartidores(self),
            "seguimiento": CapitanSeguimiento(self),
            "indicadores": CapitanIndicadores(self)
        }

    def _select_capitan(self, directive: dict):
        # Recibe directiva_original (dict)
        parameters = directive.get("parameters", {})
        target = parameters.get("target_area", "").lower()

        if target == "despacho" or "asignar" in target:
            return self.capitanes["despacho"]
        if target == "rutas" or "ruta" in target:
            return self.capitanes["rutas"]
        if target == "repartidores" or "conductor" in target:
            return self.capitanes["repartidores"]
        if target == "seguimiento" or "track" in target:
            return self.capitanes["seguimiento"]
        if target == "indicadores" or "kpi" in target:
            return self.capitanes["indicadores"]

        return self.capitanes["despacho"]
