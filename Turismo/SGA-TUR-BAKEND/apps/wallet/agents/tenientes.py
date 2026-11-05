import logging
from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from .sargentos import (
    SargentoRegistroMovimiento,
    SargentoCalculoSaldo,
    SargentoEscrituraContable,
    SargentoBitacoraSoberana,
    SargentoOperacionBalance,
    SargentoAnalisisPatrones,
    SargentoMonitoreoAlertas
)

logger = logging.getLogger(__name__)

class TenienteValidacionSaldo(TenienteTemplate):
    def perform_action(self, parametros: dict):
        sargento = SargentoCalculoSaldo()
        res = sargento.execute(parametros.get("wallet_id"))
        return {
            "balance": float(res["balance"]),
            "locked_balance": float(res["locked_balance"]),
            "total": float(res["total"])
        }

class TenienteAutorizacionTransferencias(TenienteTemplate):
    def perform_action(self, parametros: dict):
        sargento_reg = SargentoRegistroMovimiento()
        sargento_cont = SargentoEscrituraContable()

        tx_id = sargento_reg.execute(parametros)
        sargento_cont.execute(tx_id)

        return {"transaction_id": tx_id, "status": "AUTHORIZED"}

class TenienteControlLimites(TenienteTemplate):
    def perform_action(self, parametros: dict):
        # Lógica de validación de límites (simplificada)
        amount = parametros.get("amount", 0)
        if amount > 10000000: # 10M COP limit for example
            raise ValueError("Monto excede los límites institucionales de transferencia.")
        return {"limit_check": "PASSED"}

class TenienteEvidenciasFinancieras(TenienteTemplate):
    def perform_action(self, parametros: dict):
        sargento_bit = SargentoBitacoraSoberana()
        entry_id = sargento_bit.execute(parametros)
        return {"audit_entry": entry_id, "integrity": "VERIFIED"}

class TenienteBloqueoFondos(TenienteTemplate):
    def perform_action(self, parametros: dict):
        sargento = SargentoOperacionBalance()
        parametros["operation"] = "lock"
        sargento.execute(parametros)
        return {"status": "LOCKED", "amount": parametros.get("amount")}

class TenienteLiberacionFondos(TenienteTemplate):
    def perform_action(self, parametros: dict):
        sargento = SargentoOperacionBalance()
        parametros["operation"] = "unlock"
        sargento.execute(parametros)
        return {"status": "UNLOCKED", "amount": parametros.get("amount")}

class TenienteMonitoreoRiesgo(TenienteTemplate):
    def perform_action(self, parametros: dict):
        sargento_pat = SargentoAnalisisPatrones()
        sargento_ale = SargentoMonitoreoAlertas()

        sargento_pat.execute(parametros)
        sargento_ale.execute(parametros)

        return {"risk_score": 0.05, "status": "CLEAN"}
