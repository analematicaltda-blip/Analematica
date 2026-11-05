import hashlib
import json
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class AuditEngine:
    """
    Motor de Auditoría Soberano del Core ERP.
    Garantiza la inmutabilidad de los registros críticos mediante encadenamiento hash.
    """

    @staticmethod
    def generate_hash(data, previous_hash):
        """
        Genera un hash SHA-256 combinando los datos y el hash anterior.
        """
        payload = json.dumps(data, sort_keys=True, default=str)
        content = f"{payload}{previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def record_critical_action(action, entity_type, entity_id, payload, user_id, previous_hash=None):
        """
        Crea un registro de auditoría inmutable.
        """
        # 1. Preparar datos para el hash
        audit_data = {
            'action': action,
            'entity_type': entity_type,
            'entity_id': str(entity_id),
            'payload': payload,
            'user_id': user_id,
            'timestamp': str(timezone.now())
        }

        # 2. Calcular Integridad
        integrity_hash = AuditEngine.generate_hash(audit_data, previous_hash or "")

        logger.info(f"Registro de Auditoría Generado: {action} sobre {entity_type}:{entity_id}")

        # En una implementación real, aquí se guardaría en el modelo BaseAuditTrail
        return integrity_hash

    @staticmethod
    def verify_chain(logs):
        """
        Verifica la integridad de una cadena de registros de auditoría.
        """
        if not logs:
            return True, "Chain empty"

        previous_hash = ""
        for i, log in enumerate(logs):
            # Asumimos que log tiene data_json y integrity_hash
            calculated_hash = AuditEngine.generate_hash(log.data_json, previous_hash)
            if calculated_hash != log.integrity_hash:
                return False, f"Integrity break at sequence {i} (ID: {log.id})"
            previous_hash = log.integrity_hash

        return True, "Integrity verified"
