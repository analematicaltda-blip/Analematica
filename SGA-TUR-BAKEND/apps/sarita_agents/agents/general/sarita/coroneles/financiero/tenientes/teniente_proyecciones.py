# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/tenientes/teniente_proyecciones.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
import logging

logger = logging.getLogger(__name__)

from ..sargentos.sargento_proyecciones import SargentoProyecciones

class TenienteProyecciones(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE PROYECCIONES
    Modelado de escenarios y tendencias.
    """
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"CAPITÁN PROYECCIONES: Generando modelos predictivos.")
        sargento = SargentoProyecciones(teniente=self)
        return sargento.handle_order(parametros)
