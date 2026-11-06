# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/tenientes/teniente_impuestos.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargento_impuestos import SargentoImpuestos
import logging

logger = logging.getLogger(__name__)

class TenienteImpuestos(TenienteTemplate):
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"TENIENTE IMPUESTOS: Supervisando cumplimiento fiscal.")
        sargento = SargentoImpuestos(teniente=self)
        return sargento.handle_order(parametros)
