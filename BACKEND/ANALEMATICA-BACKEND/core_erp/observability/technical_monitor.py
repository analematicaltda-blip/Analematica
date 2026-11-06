import psutil
import logging
import time
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

class TechnicalMonitor:
    """
    Monitor Técnico en Vivo (Fase 4.6).
    Captura métricas de infraestructura y emite alertas de degradación.
    """
    @staticmethod
    def capture_system_metrics():
        try:
            cpu_usage = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()

            metrics = {
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": psutil.disk_usage('/').percent
            }

            # Emitir evento técnico
            severity = "info"
            if cpu_usage > 85 or memory.percent > 90:
                severity = "warning"
            if cpu_usage > 95:
                severity = "critical"

            EventBus.emit(
                "TechnicalMetricsUpdated",
                metrics,
                severity=severity
            )

            logger.info(f"Monitor: Métricas capturadas - CPU: {cpu_usage}% MEM: {memory.percent}%")
            return metrics
        except Exception as e:
            logger.error(f"Monitor Error: {e}")
            return None

    @staticmethod
    def monitor_latency(func):
        """
        Decorator para medir latencia de funciones críticas (ej. API IA).
        """
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start

            if duration > 5.0: # Umbral de 5 segundos
                EventBus.emit(
                    "DegradacionServicioIA",
                    {"duration": duration, "function": func.__name__},
                    severity="warning"
                )

            return result
        return wrapper
