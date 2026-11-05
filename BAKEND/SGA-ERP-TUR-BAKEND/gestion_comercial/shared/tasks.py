import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import DomainEvent
from .subscribers import get_subscribers_for_event

logger = logging.getLogger(__name__)

@shared_task
def process_pending_events():
    """
    Procesa todos los eventos de dominio pendientes.
    Esta tarea debería ser llamada periódicamente (ej. cada 10 segundos).
    """
    pending_events = DomainEvent.objects.filter(status='pending').order_by('created_at')

    with transaction.atomic():
        # Bloqueamos los eventos para evitar procesamiento duplicado por workers concurrentes
        events_to_process = list(pending_events.select_for_update(skip_locked=True)[:10]) # Procesar en lotes de 10

    logger.info(f"Processing {len(events_to_process)} pending domain events.")

    for event in events_to_process:
        handlers = get_subscribers_for_event(event.event_type)
        if not handlers:
            logger.warning(f"No subscribers found for event type: {event.event_type}")
            event.status = 'processed' # Marcar como procesado aunque no haya suscriptores
            event.processed_at = timezone.now()
            event.save()
            continue

        try:
            for handler in handlers:
                logger.info(f"Executing handler {handler.__name__} for event {event.id}")
                handler(event.payload)

            event.status = 'processed'
            event.processed_at = timezone.now()
        except Exception as e:
            logger.error(f"Error processing event {event.id}: {e}", exc_info=True)
            event.status = 'failed'
            event.error_message = str(e)
        finally:
            event.save()
