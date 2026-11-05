import json
import logging
import datetime
from django.utils import timezone

class EnterpriseJSONFormatter(logging.Formatter):
    """
    Fase 4: Observabilidad Total.
    Formatea los logs en JSON estructurado para ingesta empresarial.
    Incluye metadatos de contexto como correlation_id y tenant_id.
    """
    def format(self, record):
        from .middleware import get_correlation_id, get_current_tenant_id

        log_data = {
            "timestamp": timezone.now().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
            "tenant_id": get_current_tenant_id(),
            "source": f"{record.pathname}:{record.lineno}",
            "function": record.funcName
        }

        # Incluir campos extras pasados vía 'extra={...}'
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)
