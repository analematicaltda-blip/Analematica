import logging
from django.utils import timezone
from .usage_event_model import UsageEvent
from .usage_metric_model import UsageMetric
from apps.commercial_engine.models import SaaSSubscription
from apps.core_erp.event_bus import EventBus
from apps.core_erp.audit_engine import AuditEngine

logger = logging.getLogger(__name__)

class UsageCollector:
    """
    Punto de entrada para el registro de consumo real en el sistema.
    Garantiza validación y trazabilidad.
    """

    @staticmethod
    def record_usage(subscription_id, metric_code, quantity, source, idempotency_key, metadata=None):
        """
        Registra un evento de uso.
        """
        try:
            # 1. Validar Métrica
            metric = UsageMetric.objects.get(code=metric_code, is_active=True)

            # 2. Validar Suscripción
            subscription = SaaSSubscription.objects.get(id=subscription_id, is_active=True)

            # 3. Crear Evento (Idempotente por base de datos)
            event, created = UsageEvent.objects.get_or_create(
                idempotency_key=idempotency_key,
                defaults={
                    'subscription': subscription,
                    'metric': metric,
                    'quantity': quantity,
                    'timestamp': timezone.now(),
                    'source': source,
                    'metadata': metadata or {}
                }
            )

            if not created:
                logger.warning(f"Evento duplicado ignorado: {idempotency_key}")
                return event

            # 4. Auditoría Core
            AuditEngine.record_critical_action(
                action='USAGE_RECORDED',
                entity_type='UsageEvent',
                entity_id=event.id,
                payload={
                    'subscription_id': str(subscription_id),
                    'metric': metric_code,
                    'quantity': float(quantity)
                },
                user_id=f"collector_{source}"
            )

            # 5. Notificar al sistema
            EventBus.emit('USAGE_RECORDED', {
                'event_id': str(event.id),
                'subscription_id': str(subscription_id),
                'metric_code': metric_code,
                'quantity': float(quantity)
            })

            return event

        except UsageMetric.DoesNotExist:
            logger.error(f"Métrica no válida o inactiva: {metric_code}")
            raise ValueError(f"Metric {metric_code} not found.")
        except SaaSSubscription.DoesNotExist:
            logger.error(f"Suscripción no válida o inactiva: {subscription_id}")
            raise ValueError(f"Subscription {subscription_id} not found.")
        except Exception as e:
            logger.error(f"Error registrando uso: {str(e)}")
            raise e
