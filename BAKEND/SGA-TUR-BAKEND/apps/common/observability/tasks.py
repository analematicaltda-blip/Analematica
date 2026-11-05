from celery import shared_task
import logging
from .metrics import TechnicalMonitor

logger = logging.getLogger(__name__)

@shared_task(name="broadcast_system_metrics_task")
def broadcast_system_metrics_task():
    """
    Tarea periódica para emitir el pulso técnico del sistema.
    """
    try:
        TechnicalMonitor.broadcast_metrics()
    except Exception as e:
        logger.error(f"Error en tarea de métricas: {e}")

@shared_task(name="task_dispatch_distributed_event", bind=True, max_retries=5)
def task_dispatch_distributed_event(self, event_type, payload, audit_log_id):
    """
    Fase 8: Worker Distribuido.
    Ejecuta suscriptores de eventos en un proceso separado para resiliencia y escalabilidad.
    """
    from apps.core_erp.event_bus import EventBus
    from apps.core_erp.models import EventAuditLog
    import time

    logger.info(f"Worker: Procesando evento distribuido {event_type} (Log: {audit_log_id})")

    try:
        subscribers = EventBus._subscribers.get(event_type, [])
        if not subscribers:
            logger.info(f"Worker: No hay suscriptores para {event_type}. Finalizando.")
            return True

        for callback in subscribers:
            # Reintento síncrono local dentro del worker para cada callback
            success = False
            for attempt in range(3):
                try:
                    callback(payload)
                    success = True
                    break
                except Exception as e:
                    logger.warning(f"Worker: Intento {attempt+1} fallido para callback en {event_type}: {e}")
                    time.sleep(1)

            if not success:
                raise Exception(f"Callback falló tras reintentos locales en worker.")

        # Actualizar estado en el log de auditoría
        EventAuditLog.objects.filter(id=audit_log_id).update(status='PROCESSED')
        return True

    except Exception as exc:
        logger.error(f"Worker: Fallo crítico en procesamiento distribuido de {event_type}: {exc}")
        # Reintento de toda la tarea en Celery con backoff
        raise self.retry(exc=exc, countdown=60)
