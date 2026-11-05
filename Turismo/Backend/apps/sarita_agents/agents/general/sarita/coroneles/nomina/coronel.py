from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from .capitanes.capitan_gestion_laboral import CapitanGestionLaboral

class CoronelNomina(CoronelTemplate):
    """
    NIVEL 2 — GENERAL DE NÓMINA
    Control macro del costo laboral y cumplimiento legal.
    """
    def __init__(self, general, domain="nomina"):
        super().__init__(general=general, domain=domain)

    def _get_capitanes(self) -> dict:
        return {
            "gestion_laboral": CapitanGestionLaboral(coronel=self)
        }

    def _select_capitan(self, directiva: dict):
        return self.capitanes.get("gestion_laboral")
