# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/coronel.py

from .....coronel_template import CoronelTemplate
from .capitanes.capitan_tesoreria_y_planeacion import CapitanTesoreriaYPlaneacion

class CoronelFinanciero(CoronelTemplate):
    """
    NIVEL 2 — GENERAL FINANCIERO
    Control macro de liquidez, aprobación de presupuestos y supervisión de endeudamiento.
    """
    def __init__(self, general):
        super().__init__(general=general, domain="finanzas")

    def _get_capitanes(self) -> dict:
        return {
            "tesoreria_y_planeacion": CapitanTesoreriaYPlaneacion(coronel=self)
        }

    def _select_capitan(self, directiva: dict):
        return self.capitanes.get("tesoreria_y_planeacion")
