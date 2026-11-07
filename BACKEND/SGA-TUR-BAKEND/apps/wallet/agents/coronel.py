import logging
from apps.sarita_agents.agents.coronel_template import CoronelTemplate
from .capitanes import (
    CapitanCustodiaFondos,
    CapitanTransferencias,
    CapitanPagosServicios,
    CapitanLiquidaciones,
    CapitanAuditoriaFinanciera,
    CapitanAntifraude
)

logger = logging.getLogger(__name__)

class CoronelMonedero(CoronelTemplate):
    def __init__(self, general):
        super().__init__(general, domain="wallet")

    def _get_capitanes(self) -> dict:
        return {
            "custodia": CapitanCustodiaFondos(self),
            "transferencias": CapitanTransferencias(self),
            "pagos": CapitanPagosServicios(self),
            "liquidaciones": CapitanLiquidaciones(self),
            "auditoria": CapitanAuditoriaFinanciera(self),
            "antifraude": CapitanAntifraude(self)
        }

    def _select_capitan(self, mission: dict):
        action = mission.get("action", "").lower()
        if "custodia" in action or "saldo" in action:
            return self.capitanes["custodia"]
        if "transferir" in action or "enviar" in action:
            return self.capitanes["transferencias"]
        if "pagar" in action or "servicio" in action:
            return self.capitanes["pagos"]
        if "liquidar" in action:
            return self.capitanes["liquidaciones"]
        if "auditar" in action or "verificar" in action:
            return self.capitanes["auditoria"]
        if "fraude" in action or "riesgo" in action:
            return self.capitanes["antifraude"]

        return self.capitanes["auditoria"] # Default to audit for unknown actions
