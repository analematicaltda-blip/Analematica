from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from .capitanes.capitan_seguridad import CapitanSeguridad

class CoronelSST(CoronelTemplate):
    """
    NIVEL 2 — GENERAL SGSST
    Control macro del sistema, validación de indicadores y supervisión de riesgos.
    """
    def __init__(self, general, domain="sg_sst"):
        super().__init__(general=general, domain=domain)

    def _get_capitanes(self) -> dict:
        return {
            "seguridad": CapitanSeguridad(coronel=self)
        }

    def _select_capitan(self, directiva: dict):
        return self.capitanes.get("seguridad")
