# backend/apps/sarita_agents/agents/general/sarita/coroneles/clientes_turistas/sargentos/sargento_turista.py

from apps.sarita_agents.agents.sargento_template import SargentoTemplate
import logging

logger = logging.getLogger(__name__)

class SargentoAtencionTurista(SargentoTemplate):
    """Interfaz entre los agentes de turista y la lógica de perfil/experiencia."""
    def handle_mission(self, params: dict):
        logger.info("SARGENTO TURISTA: Coordinando experiencia del viajero.")
        return {"result": "Experiencia personalizada en proceso."}
