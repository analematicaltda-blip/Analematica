# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/tenientes/teniente_indicadores.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
import logging

logger = logging.getLogger(__name__)

from ..sargentos.sargento_indicadores import SargentoIndicadores

class TenienteIndicadores(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE INDICADORES
    Monitoreo de KPIs financieros (EBITDA, Liquidez, etc).
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"CAPITÁN INDICADORES: Recalculando métricas de salud.")
        sargento = SargentoIndicadores(teniente=self)
        return sargento.handle_order(parametros)
