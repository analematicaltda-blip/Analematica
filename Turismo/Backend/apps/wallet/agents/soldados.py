from apps.sarita_agents.agents.soldado_template import SoldierTemplate
import logging

logger = logging.getLogger(__name__)

class SoldadoAuditor(SoldierTemplate):
    """ NIVEL 6 — SOLDADO AUDITOR DE WALLET """
    def __init__(self, sargento, id):
        super().__init__(sargento)
        self.soldier_id = id

    def perform_action(self, params: dict):
        logger.info(f"SOLDADO AUDITOR #{self.soldier_id}: Verificando integridad de Ledger.")
        return {"status": "SUCCESS", "soldier": self.soldier_id, "task": "LEDGER_VERIFICATION"}

class SoldadoAnalista(SoldierTemplate):
    """ NIVEL 6 — SOLDADO ANALISTA ANTIFRAUDE """
    def __init__(self, sargento, id):
        super().__init__(sargento)
        self.soldier_id = id

    def perform_action(self, params: dict):
        logger.info(f"SOLDADO ANALISTA #{self.soldier_id}: Analizando patrones de geolocalización de transacciones.")
        return {"status": "SUCCESS", "soldier": self.soldier_id, "task": "GEO_ANALYSIS"}

class SoldadoVigilante(SoldierTemplate):
    """ NIVEL 6 — SOLDADO VIGILANTE FINANCIERO """
    def __init__(self, sargento, id):
        super().__init__(sargento)
        self.soldier_id = id

    def perform_action(self, params: dict):
        logger.info(f"SOLDADO VIGILANTE #{self.soldier_id}: Monitoreando picos de retiros inusuales.")
        return {"status": "SUCCESS", "soldier": self.soldier_id, "task": "WITHDRAW_MONITORING"}
