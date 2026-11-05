# backend/apps/sadi_agent/security.py
import logging
from api.models import CustomUser
from .models import VoicePermission, Intent

logger = logging.getLogger(__name__)

class VoiceSecurity:
    """
    Servicio para manejar la autorización de acciones de voz.
    """

    def is_authorized(self, user: CustomUser, intent: Intent) -> bool:
        """
        Verifica si un usuario tiene permiso para ejecutar una intención.
        """
        if not user or not intent:
            return False

        user_role = user.role
        required_domain = intent.domain.name
        required_action = intent.name

        logger.debug(
            f"Verificando permiso: Rol='{user_role}', "
            f"Dominio='{required_domain}', Acción='{required_action}'"
        )

        # La lógica de permisos es simple: si existe un registro que coincida,
        # el permiso es concedido. Si no, es denegado.
        has_permission = VoicePermission.objects.filter(
            role=user_role,
            domain=required_domain,
            action=required_action
        ).exists()

        if has_permission:
            logger.info("Permiso concedido.")
        else:
            logger.warning("Permiso denegado.")

        return has_permission
