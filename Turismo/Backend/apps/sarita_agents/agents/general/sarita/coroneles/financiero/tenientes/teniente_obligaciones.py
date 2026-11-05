# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/tenientes/teniente_obligaciones.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
import logging

logger = logging.getLogger(__name__)

from ..sargentos.sargento_obligaciones import SargentoObligaciones

class TenienteObligaciones(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE OBLIGACIONES
    Seguimiento de deudas, créditos y compromisos financieros.
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"CAPITÁN OBLIGACIONES: Supervisando tabla de amortización.")
        sargento = SargentoObligaciones(teniente=self)
        return sargento.handle_order(parametros)
