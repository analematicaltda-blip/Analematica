# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/tenientes/teniente_facturacion.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargento_facturacion import SargentoFacturacion
import logging

logger = logging.getLogger(__name__)

class TenienteFacturacion(TenienteTemplate):
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"TENIENTE FACTURACIÓN: Supervisando ciclo de facturación.")
        sargento = SargentoFacturacion(teniente=self)
        return sargento.handle_order(parametros)
