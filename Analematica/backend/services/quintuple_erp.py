import logging
from django.utils import timezone
from api.models import CustomUser

logger = logging.getLogger(__name__)

class QuintupleERPService:
    """
    Servicio centralizado para asegurar el impacto en las 5 dimensiones del ERP SARITA.
    REFACTORED FASE 1: Comunicación vía Eventos (Decoupled).
    """
    def __init__(self, user: CustomUser):
        self.user = user

    def record_impact(self, event_type: str, payload: dict):
        """
        Punto de entrada único para la propagación de impacto sistémico.
        Ahora emite un evento al EventBus para desacoplar los dominios.
        """
        logger.info(f"FASE 1 (DECOUPLED ERP): Solicitando impacto '{event_type}'")

        from apps.core_erp.event_bus import EventBus
        from apps.core_erp.events.erp_events import ErpImpactRequested

        event = ErpImpactRequested(
            event_type=event_type,
            payload=payload,
            user_id=self.user.id if self.user else None
        )

        # Emitimos el evento. Los dominios interesados (Comercial, Contable, etc.)
        # deben estar suscritos y procesar su parte de forma independiente.

        # El EventBus espera un payload (dict), no una instancia de dataclass directamente.
        payload_dict = {
            "event_type": event_type,
            "payload": payload,
            "user_id": self.user.id if self.user else None,
            "event_id": str(event.event_id)
        }

        EventBus.emit("ERP_IMPACT_REQUESTED", payload_dict)

        # Retornamos un resultado parcial, ya que la ejecución ahora es desacoplada
        return {
            "status": "IMPACT_REQUESTED",
            "correlation_id": str(event.event_id),
            "timestamp": event.timestamp.isoformat()
        }
