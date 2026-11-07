# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/tenientes/teniente_cartera.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargento_cartera import SargentoCartera
import logging

logger = logging.getLogger(__name__)

class TenienteCartera(TenienteTemplate):
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"TENIENTE CARTERA: Supervisando recuperación de cartera.")
        sargento = SargentoCartera(teniente=self)
        return sargento.handle_order(parametros)
