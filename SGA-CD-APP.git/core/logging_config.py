import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict

SENSITIVE_PATTERNS = [
    (re.compile(r'(?i)(\\?"(?:password|clave|contraseña|token|access_token|secret|authorization)\\?"\s*:\s*\\?")[^"\\]+(\\?")'), r'\1[REDACTADO]\2'),
    (re.compile(r'(?i)Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*'), r'Bearer [TOKEN_REDACTADO]'),
    (re.compile(r'\b(?:\d[ -]*?){13,19}\b'), r'[TARJETA_CREDITO_REDACTADA]'),
]

class JSONStructuredFormatter(logging.Formatter):
    """
    Structured JSON log formatter for SGA-CD system observability.
    Redacts sensitive keys (passwords, tokens, cards) automatically.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include request context if present
        for attr in ("correlation_id", "method", "path", "status_code", "duration_ms", "client_ip"):
            if hasattr(record, attr):
                log_obj[attr] = getattr(record, attr)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        raw_json = json.dumps(log_obj, ensure_ascii=False)

        # Apply privacy redactions
        for pattern, replacement in SENSITIVE_PATTERNS:
            raw_json = pattern.sub(replacement, raw_json)

        return raw_json

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONStructuredFormatter())
        logger.addHandler(handler)

    return logger
