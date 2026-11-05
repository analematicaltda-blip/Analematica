import logging
from django.utils import timezone
from .models import AuditLog, SystemAuditLog

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Servicio centralizado para el registro de auditoría.
    """
    @staticmethod
    def log(user, action, request=None, details=None, company=None):
        """
        Registra una acción en el log de auditoría.
        """
        if details is None:
            details = {}

        username = user.username if user else "system"
        ip_address = None

        if request:
            # Intentar obtener la IP del request
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

        return AuditLog.objects.create(
            user=user,
            username=username,
            action=action,
            ip_address=ip_address,
            details=details,
            company=company
        )

class AuditService:
    @staticmethod
    def log(user, action, entity, entity_id, ip_address, old=None, new=None):
        return SystemAuditLog.objects.create(
            user=user,
            action=action,
            entity=entity,
            entity_id=str(entity_id),
            ip_address=ip_address,
            old_values=old,
            new_values=new
        )
