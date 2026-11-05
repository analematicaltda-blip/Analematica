# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/tenientes/teniente_presupuestos.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargento_presupuesto import SargentoPresupuesto
import logging

logger = logging.getLogger(__name__)

class TenientePresupuestos(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE PRESUPUESTOS
    Control de ejecución y detección de desviaciones.
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"CAPITÁN PRESUPUESTO: Validando ejecución presupuestal.")
        sargento = SargentoPresupuesto(teniente=self)
        return sargento.handle_order(parametros)
