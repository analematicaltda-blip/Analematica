import os
import django
import uuid
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puerto_gaitan_turismo.settings")
django.setup()

from apps.core_erp.event_bus import EventBus
from apps.core_erp.models import EventAuditLog

def test_emit():
    print("Iniciando prueba de EventBus...")
    payload = {"test": "data", "entity_id": "test-entity-001"}

    try:
        # Esto debería fallar si la tabla no existe o el modelo está mal
        EventBus.emit("TestEvent", payload, severity="warning")
        print("Evento emitido exitosamente.")

        log = EventAuditLog.objects.filter(event_type="TestEvent").first()
        if log:
            print(f"Log encontrado: {log.id} - Severity: {log.severity}")
        else:
            print("Log NO encontrado en DB.")

    except Exception as e:
        print(f"Error en prueba: {e}")

if __name__ == "__main__":
    test_emit()
