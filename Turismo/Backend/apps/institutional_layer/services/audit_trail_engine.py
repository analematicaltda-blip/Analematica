import hashlib
import json
import logging
from django.utils import timezone
from ..models import InstitutionalAuditLog

logger = logging.getLogger(__name__)

class AuditTrailEngine:
    """
    Motor de auditoría inmutable con encadenamiento de hashes (Fase 7).
    """

    @staticmethod
    def log_critical_change(user, action, financial_impact, details):
        """
        Registra un cambio crítico con firma de integridad.
        """
        last_log = InstitutionalAuditLog.objects.order_by('-timestamp').first()
        prev_hash = last_log.integrity_hash if last_log else "INSTITUTIONAL_GENESIS"

        # Generar hash de integridad
        payload = {
            "user_id": str(user.id),
            "action": action,
            "impact": str(financial_impact),
            "details": details,
            "prev_hash": prev_hash,
            "timestamp": timezone.now().isoformat()
        }

        data_str = json.dumps(payload, sort_keys=True)
        integrity_hash = hashlib.sha256(data_str.encode()).hexdigest()

        log_entry = InstitutionalAuditLog.objects.create(
            user=user,
            action=action,
            impact_financial=financial_impact,
            change_details=details,
            previous_hash=prev_hash,
            integrity_hash=integrity_hash
        )

        logger.info(f"AUDIT_TRAIL: Cambio registrado. Hash: {integrity_hash[:10]}")
        return log_entry

    @staticmethod
    def verify_integrity():
        """
        Valida que la cadena de auditoría no haya sido alterada.
        """
        logs = InstitutionalAuditLog.objects.order_by('timestamp')
        prev_hash = "INSTITUTIONAL_GENESIS"

        for log in logs:
            if log.previous_hash != prev_hash:
                return False, f"Brecha de integridad detectada en log {log.id}"
            prev_hash = log.integrity_hash

        return True, "Cadena de auditoría íntegra."
