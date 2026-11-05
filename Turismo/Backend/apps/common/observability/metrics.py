import psutil
import logging
from django.utils import timezone
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class TechnicalMonitor:
    """
    Fase 4: Observabilidad Total.
    Colecta métricas de infraestructura y rendimiento del sistema.
    """
    @staticmethod
    def get_system_metrics():
        return {
            "cpu_usage_percent": psutil.cpu_percent(interval=1),
            "ram_usage_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "timestamp": timezone.now().isoformat()
        }

    @staticmethod
    def broadcast_metrics():
        metrics = TechnicalMonitor.get_system_metrics()
        logger.info(f"Métricas de sistema recolectadas: CPU {metrics['cpu_usage_percent']}%", extra_fields={"metrics": metrics})

        # Propagar a la Torre de Control vía EventBus
        EventBus.emit(
            event_type="TECHNICAL_METRICS_UPDATED",
            payload=metrics,
            severity="info"
        )
        return metrics

class BusinessMonitor:
    """
    Fase 4: Observabilidad Total.
    Colecta métricas de negocio en tiempo real.
    """
    @staticmethod
    def get_realtime_kpis():
        # Aquí se integrarían consultas rápidas al ReportsEngine o Redis
        return {
            "active_users_24h": 0, # Placeholder para integración con sesiones
            "transactions_today": 0, # Placeholder
            "system_error_rate": 0.0,
            "timestamp": timezone.now().isoformat()
        }
