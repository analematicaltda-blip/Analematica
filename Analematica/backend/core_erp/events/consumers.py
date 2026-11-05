import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger(__name__)

class TowerConsumer(AsyncWebsocketConsumer):
    """
    Consumer para la Torre de Control Omnisciente.
    Maneja suscripciones a eventos de holding y entidad.
    """
    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            logger.warning("WebSocket: Intento de conexión no autenticado.")
            await self.close()
            return

        # Grupos por defecto
        self.groups_joined = []

        # 1. Grupo Global (Solo SuperAdmin)
        if self.user.role == 'SUPERADMIN' or self.user.is_superuser:
            await self.channel_layer.group_add("sarita_tower_global", self.channel_name)
            self.groups_joined.append("sarita_tower_global")
            logger.info(f"WebSocket: SuperAdmin {self.user.email} unido a sarita_tower_global")

        # 2. Grupo por Entidad (Aislamiento Multiempresa)
        # Se asume que el usuario tiene un entity_id o perfil_id
        entity_id = None
        if hasattr(self.user, 'perfil_prestador') and self.user.perfil_prestador:
            entity_id = str(self.user.perfil_prestador.id)

        if entity_id:
            group_name = f"sarita_entity_{entity_id}"
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.groups_joined.append(group_name)
            logger.info(f"WebSocket: Usuario {self.user.email} unido a {group_name}")

        await self.accept()

    async def disconnect(self, close_code):
        for group in self.groups_joined:
            await self.channel_layer.group_discard(group, self.channel_name)
        logger.info(f"WebSocket: Usuario {self.user.email} desconectado.")

    async def broadcast_event(self, event):
        """
        Envía el evento al cliente WebSocket.
        """
        await self.send(text_data=json.dumps(event["event"]))

    async def receive(self, text_data):
        # Por ahora no manejamos mensajes desde el cliente (Omnisciencia es push)
        pass
