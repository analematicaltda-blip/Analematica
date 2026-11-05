from django.db import models
import uuid
import hashlib
import json
from django.utils import timezone

class AlgorithmicCertificate(models.Model):
    """
    Certificado de Confianza Algorítmica (Z-TRUST-NET).
    Representa una prueba firmada de la integridad y cumplimiento de un nodo soberano.
    """
    class CertificateType(models.TextChoices):
        GOVERNANCE = 'GOVERNANCE', 'Certificado de Gobernanza'
        AUDIT = 'AUDIT', 'Certificado de Auditoría'
        NEUTRALITY = 'NEUTRALITY', 'Certificado de Neutralidad'
        SECURITY = 'SECURITY', 'Certificado de Seguridad'
        HUMAN_RIGHTS = 'HUMAN_RIGHTS', 'Certificado de Derechos Humanos'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node_id = models.CharField(max_length=100, help_text="ID del Nodo Nacional emisor")
    type = models.CharField(max_length=20, choices=CertificateType.choices)
    issued_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    # Datos que respaldan el certificado (ej: métricas agregadas)
    evidence_summary = models.JSONField()

    # Firma criptográfica del certificado
    signature = models.TextField(help_text="Firma SHA-256 del contenido del certificado")
    is_revoked = models.BooleanField(default=False)
    revocation_reason = models.TextField(null=True, blank=True)

    def generate_signature(self, private_key=None):
        """Genera una firma determinista para el certificado."""
        if not private_key:
            from django.conf import settings
            private_key = getattr(settings, "SARITA_NODE_PRIVATE_KEY", "SARITA_FALLBACK_KEY_STABLE_Z")

        payload = f"{self.node_id}{self.type}{self.issued_at.isoformat()}{json.dumps(self.evidence_summary)}"
        # En una implementación real, se usaría RSA/ECDSA con la llave privada del nodo
        self.signature = hashlib.sha256((payload + private_key).encode()).hexdigest()

    def __str__(self):
        return f"{self.type} - {self.node_id} ({self.issued_at.date()})"

class TrustSignal(models.Model):
    """
    Señales de Confianza Compartidas.
    Indicadores de alto nivel compartidos entre estados para alertas tempranas.
    """
    class SignalLevel(models.TextChoices):
        STABLE = 'STABLE', 'Estable'
        WARNING = 'WARNING', 'Advertencia'
        CRITICAL = 'CRITICAL', 'Crítica'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    origin_node = models.CharField(max_length=100)
    category = models.CharField(max_length=50, help_text="Ej: CIBERSEGURIDAD, ESTABILIDAD_ECONOMICA")
    level = models.CharField(max_length=20, choices=SignalLevel.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    # Metadatos anonimizados
    metadata = models.JSONField(default=dict)

    # Hash de validación para asegurar que la señal no fue alterada en tránsito
    verification_hash = models.CharField(max_length=64)

    def save(self, *args, **kwargs):
        if not self.verification_hash:
            payload = f"{self.origin_node}{self.category}{self.level}{self.description}"
            self.verification_hash = hashlib.sha256(payload.encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.level}] {self.category} de {self.origin_node}"
