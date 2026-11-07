# backend/apps/sarita_agents/agents/general/sarita/coroneles/contable/coronel.py

from .....coronel_template import CoronelTemplate
from .capitanes.capitan_contable import CapitanContable

class CoronelContable(CoronelTemplate):
    """
    NIVEL 2 — CORONEL CONTABLE
    Responsable del dominio funcional contable.
    Interpreta directrices y emite órdenes estructurales.
    """
    def __init__(self, general):
        super().__init__(general=general, domain="contabilidad")

    def _get_capitanes(self) -> dict:
        return {
            "contable_general": CapitanContable(coronel=self)
        }

    def _select_capitan(self, directiva: dict):
        # Por ahora, todas las misiones contables van al CapitanContable general
        return self.capitanes.get("contable_general")
