# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/tenientes/teniente_inventario.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargento_inventario import SargentoInventario
import logging

logger = logging.getLogger(__name__)

class TenienteInventario(TenienteTemplate):
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"TENIENTE INVENTARIO: Gestionando control de stock.")
        sargento = SargentoInventario(teniente=self)
        return sargento.handle_order(parametros)
