# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/tenientes/teniente_tesoreria.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargento_flujo_real import SargentoFlujoReal
from ..sargentos.sargento_conciliaciones import SargentoConciliaciones
import logging

logger = logging.getLogger(__name__)

class TenienteTesoreria(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE TESORERÍA
    Responsable de la ejecución operativa de flujos y conciliaciones.
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"CAPITÁN TESORERÍA: Gestionando flujo de caja.")

        # Delegación dual según parámetros
        if parametros.get("sub_task") == "conciliacion":
            sargento = SargentoConciliaciones(teniente=self)
        else:
            sargento = SargentoFlujoReal(teniente=self)

        return sargento.handle_order(parametros)
