import time
import psutil
from django.db import connections
from django.db.utils import OperationalError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.cache import cache
from ..metrics import TechnicalMonitor

class LivenessProbeView(APIView):
    """
    K8s Liveness Probe: El sistema está vivo (proceso Django corriendo).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "alive", "timestamp": time.time()}, status=200)


class ReadinessProbeView(APIView):
    """
    K8s Readiness Probe: El sistema está listo para recibir tráfico (DB y Redis OK).
    """
    permission_classes = [AllowAny]

    def get(self, request):
        health = {
            "database": "ok",
            "cache": "ok",
            "status": "ready"
        }
        status_code = 200

        # Check DB
        try:
            db_conn = connections['default']
            db_conn.cursor()
        except OperationalError:
            health["database"] = "down"
            health["status"] = "not_ready"
            status_code = 503

        # Check Cache (Redis)
        try:
            cache.set('readiness_check', 1, 10)
            if not cache.get('readiness_check'):
                raise Exception("Cache not returning values")
        except Exception:
            health["cache"] = "down"
            health["status"] = "not_ready"
            status_code = 503

        return Response(health, status=status_code)


class MetricsEndpointView(APIView):
    """
    Prometheus-style metrics endpoint (JSON format for Sarita Dashboard).
    """
    permission_classes = [AllowAny] # In production, restrict to internal monitoring IPs

    def get(self, request):
        metrics = TechnicalMonitor.get_system_metrics()

        # Add additional infra metrics
        metrics.update({
            "process_id": psutil.Process().pid,
            "threads": psutil.Process().num_threads(),
            "open_files": len(psutil.Process().open_files()),
            "connections": len(psutil.Process().connections()),
            "uptime_seconds": time.time() - psutil.Process().create_time()
        })

        return Response(metrics, status=200)
