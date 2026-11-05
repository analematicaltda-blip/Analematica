import logging
from django.utils import timezone
from ..models import HistoricalEvent

logger = logging.getLogger(__name__)

class DataLakeEngine:
    """
    Ingesta y gestión de eventos históricos para BI institucional (Fase 7).
    """

    @staticmethod
    def ingest_event(event_type, domain, payload, entity_id=None, tenant_id=None):
        """
        Registra un nuevo evento en el Data Lake.
        """
        event = HistoricalEvent.objects.create(
            event_type=event_type,
            domain=domain,
            payload=payload,
            timestamp=timezone.now(),
            entity_id=entity_id,
            tenant_id=tenant_id
        )
        logger.info(f"DATA_LAKE: Evento '{event_type}' registrado. ID: {event.id}")
        return event

    @staticmethod
    def get_historical_stream(domain=None, event_type=None):
        """
        Retorna un flujo de eventos para análisis.
        """
        queryset = HistoricalEvent.objects.all()
        if domain:
            queryset = queryset.filter(domain=domain)
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        return queryset
