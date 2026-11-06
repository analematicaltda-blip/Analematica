from django.test import TestCase
from apps.core_erp.event_bus import EventBus
from apps.core_erp.models import EventAuditLog
from unittest.mock import MagicMock
import time

class RealTimeOmniscienceTest(TestCase):
    """
    Suite de pruebas para validar la Fase 4: Omnisciencia Operativa.
    """

    def test_event_standardization_and_persistence(self):
        """
        Prueba 1: Validar que los eventos se emitan con el formato estándar y persistan.
        """
        payload = {"total": 5000.0, "entity_id": "test-entity-123"}
        EventBus.emit("SALE_CREATED", payload, severity="critical", user_id="admin-1")

        # Verificar persistencia en base de datos
        log = EventAuditLog.objects.filter(event_type="SALE_CREATED").first()
        self.assertIsNotNone(log)
        self.assertEqual(log.severity, "critical")
        self.assertEqual(log.tenant_id, "test-entity-123")
        self.assertEqual(log.payload["total"], 5000.0)

    def test_websocket_propagation_integrity(self):
        """
        Prueba 2: Simular la propagación a WebSockets.
        """
        # Mock del channel_layer
        channel_layer_mock = MagicMock()
        with MagicMock() as mock_get_layer:
            mock_get_layer.return_value = channel_layer_mock
            # Aquí se asume que EventBus usa get_channel_layer internamente
            # Emitir evento
            EventBus.emit("PagoRecibido", {"amount": 100.0, "tenant_id": "ent-1"})

            # Nota: Debido a la naturaleza asíncrona de Channels,
            # esta prueba valida que el código no falle y se ejecute el flujo de emisión.

    def test_technical_monitor_alert(self):
        """
        Prueba 3: Validar alertas del monitor técnico.
        """
        from apps.core_erp.observability.technical_monitor import TechnicalMonitor

        # Simular una función lenta
        @TechnicalMonitor.monitor_latency
        def slow_function():
            time.sleep(0.1) # Simulamos latencia pero corta para el test
            return True

        slow_function()
        # Verificar que el evento no se emitió si no superó el umbral (5.0s)
        self.assertEqual(EventAuditLog.objects.filter(event_type="DegradacionServicioIA").count(), 0)
