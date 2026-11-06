# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/tenientes/operativo_agencia_teniente.py

from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargento_agencia import SargentoOperativoAgencia
import logging

logger = logging.getLogger(__name__)

class TenienteOperativoAgencia(TenienteTemplate):
    def perform_action(self, parametros: dict) -> dict:
        logger.info(f"TENIENTE AGENCIA: Iniciando ejecución coordinada.")

        sargento = SargentoOperativoAgencia(teniente=self)
        sargento_report = sargento.handle_order(parametros)

        return {
            "status": "SUCCESS",
            "message": "Operación de agencia coordinada.",
            "sargento_report": sargento_report
        }
