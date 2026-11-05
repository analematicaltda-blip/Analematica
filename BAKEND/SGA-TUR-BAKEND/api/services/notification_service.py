import logging
from django.conf import settings
from ..models import DeviceToken

logger = logging.getLogger(__name__)

def send_push_notification(user_id, title, message, data=None):
    """
    Hallazgo 10: Sistema de Notificaciones Push.
    Envía una notificación a todos los dispositivos registrados de un usuario.
    Simula la integración con FCM (Firebase Cloud Messaging).
    """
    tokens = DeviceToken.objects.filter(user_id=user_id)
    if not tokens.exists():
        logger.warning(f"SARITA: No se encontraron tokens para el usuario {user_id}")
        return False

    for device in tokens:
        # En una implementación real, aquí se llamaría al SDK de Firebase
        # firebase_admin.messaging.send(message)
        logger.info(f"SARITA: Enviando Notificación [{title}] a {device.platform} (Token: {device.token[:10]}...)")

    return True

def register_device(user, token, platform):
    """
    Registra o actualiza el token de un dispositivo.
    """
    device, created = DeviceToken.objects.update_or_create(
        user=user,
        platform=platform,
        defaults={'token': token}
    )
    return device
