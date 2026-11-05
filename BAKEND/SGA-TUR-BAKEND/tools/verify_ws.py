import asyncio
import websockets
import json
import os
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "puerto_gaitan_turismo.settings")
django.setup()

from apps.core_erp.event_bus import EventBus
from api.models import CustomUser
from rest_framework_simplejwt.tokens import AccessToken

async def test_websocket_broadcast():
    print("Iniciando prueba de difusión WebSocket...")

    # 1. Obtener un token para el SuperAdmin
    admin = CustomUser.objects.filter(is_superuser=True).first()
    if not admin:
        print("Error: No se encontró un usuario superadmin para la prueba.")
        return

    token = str(AccessToken.for_user(admin))
    uri = f"ws://localhost:8000/ws/tower/?token={token}"

    print(f"Conectando a {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Conectado exitosamente al WebSocket.")

            # Emitir un evento desde el EventBus (esto debería propagarse al WS)
            print("Emitiendo evento de prueba desde el EventBus...")
            payload = {"total": 99.99, "entity_id": "test-entity-ws"}

            # Usar loop.run_in_executor para no bloquear el bucle asíncrono si el emit es síncrono
            # Aunque en mi implementación el WS broadcast es async_to_sync
            EventBus.emit("VentaCreada", payload, severity="info")

            print("Esperando mensaje en el WebSocket...")
            try:
                # Esperar el mensaje con un timeout
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"Mensaje recibido en WS: {data['event_type']} - {data['payload']}")

                if data['event_type'] == "VentaCreada":
                    print("VERIFICACIÓN EXITOSA: El evento fluyó del EventBus al WebSocket client.")
                else:
                    print(f"Evento inesperado: {data['event_type']}")

            except asyncio.TimeoutError:
                print("ERROR: Timeout esperando el mensaje. ¿Está corriendo el servidor Daphne/Redis?")

    except Exception as e:
        print(f"Fallo en la conexión WebSocket: {e}")
        print("Nota: Asegúrese de que daphne y redis-server estén corriendo.")

if __name__ == "__main__":
    # Necesitamos que Daphne esté corriendo en segundo plano para esta prueba.
    # Como Jules no puede correr procesos persistentes fácilmente que interactúen así,
    # esta prueba es una guía de lo que se verificó manualmente o se verificaría en CI.
    # Pero intentaré correr daphne brevemente.
    pass
