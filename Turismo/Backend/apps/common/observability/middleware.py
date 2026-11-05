import uuid
import threading
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from apps.core_erp.event_bus import EventBus

logger = logging.getLogger(__name__)

_thread_locals = threading.local()

def get_correlation_id():
    return getattr(_thread_locals, 'correlation_id', None)

def get_current_tenant_id():
    return getattr(_thread_locals, 'tenant_id', None)

class ObservabilityMiddleware(MiddlewareMixin):
    """
    Fase 4: Observabilidad Total.
    Inyecta Correlation ID y gestiona el contexto de observabilidad por hilo.
    """
    def process_request(self, request):
        request._start_time = time.time()
        # 1. Resolver Correlation ID (Desde header o generar uno)
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        _thread_locals.correlation_id = correlation_id
        request.correlation_id = correlation_id

        # 2. Capturar Tenant ID del request (establecido por TenantMiddleware)
        _thread_locals.tenant_id = getattr(request, 'tenant_id', None)

    def process_response(self, request, response):
        # 3. Instrumentación: Calcular latencia
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time

            # Solo loguear requests de la API
            if request.path.startswith('/api/'):
                logger.info(
                    f"API Request: {request.method} {request.path} -> {response.status_code} ({duration:.3f}s)",
                    extra={
                        "extra_fields": {
                            "path": request.path,
                            "method": request.method,
                            "status_code": response.status_code,
                            "latency": duration
                        }
                    }
                )

                # Emitir evento de latencia si es lenta (> 500ms)
                if duration > 0.5:
                    EventBus.emit(
                        event_type="SLOW_API_REQUEST",
                        payload={
                            "path": request.path,
                            "latency": duration,
                            "status": response.status_code
                        },
                        severity="warning"
                    )

        # Asegurar que el correlation_id vuelva al cliente en los headers
        if hasattr(request, 'correlation_id'):
            response['X-Correlation-ID'] = request.correlation_id

        # Limpiar thread local
        if hasattr(_thread_locals, 'correlation_id'):
            del _thread_locals.correlation_id
        if hasattr(_thread_locals, 'tenant_id'):
            del _thread_locals.tenant_id

        return response
