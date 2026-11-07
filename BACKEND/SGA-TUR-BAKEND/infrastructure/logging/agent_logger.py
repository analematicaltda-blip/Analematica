import logging
import json
from django.utils import timezone

class AgentExecutionLogger:
    """
    Sistema de logging estructurado para el monitoreo de Agentes IA.
    Captura el rastro de la inteligencia a través de las capas de servicios.
    """
    def __init__(self):
        self.logger = logging.getLogger('sarita.agents.monitoring')

    def log_action(self, agent_id, service_name, action, result):
        log_data = {
            "timestamp": timezone.now().isoformat(),
            "agent": agent_id,
            "layer": "ApplicationService",
            "service": service_name,
            "action": action,
            "success": result.success,
            "correlation_id": getattr(result, 'correlation_id', 'N/A')
        }
        self.logger.info(f"AGENT_TRACE: {json.dumps(log_data)}")

    def log_error(self, agent_id, error_msg):
        self.logger.error(f"AGENT_ERROR: Agent {agent_id} failed with error: {error_msg}")
