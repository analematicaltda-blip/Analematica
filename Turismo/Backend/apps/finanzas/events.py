import logging
from django.utils import timezone
from .models import FinancialEventRecord

logger = logging.getLogger(__name__)

class FinancialEventManager:
    """
    Gestiona la emisión y registro de eventos financieros del sistema.
    """

    @staticmethod
    def emit_event(event_type: str, session_id: str, value: float = 0.0, metadata: dict = None):
        """
        Registra un evento financiero.
        """
        logger.info(f"FINANCIAL EVENT: {event_type} | Session: {session_id} | Value: {value}")

        return FinancialEventRecord.objects.create(
            event_type=event_type,
            session_id=session_id,
            value=value,
            metadata=metadata or {},
            timestamp=timezone.now()
        )

# Tipos de Eventos
VOICE_SESSION_STARTED = 'voice_session_started'
VOICE_MINUTE_CONSUMED = 'voice_minute_consumed'
USER_REGISTERED = 'user_registered'
PLAN_ASSIGNED = 'plan_assigned'
CONVERSATION_ABANDONED = 'conversation_abandoned'
OBJECTION_DETECTED = 'objection_detected'
