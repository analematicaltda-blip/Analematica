from django.db import models
from django.conf import settings
import uuid
import hashlib
import json
from django.utils import timezone

class AuditLog(models.Model):
    class Action(models.TextChoices):
        USER_LOGIN_SUCCESS = 'USER_LOGIN_SUCCESS', 'Inicio de sesión exitoso'
        USER_LOGIN_FAILED = 'USER_LOGIN_FAILED', 'Intento de inicio de sesión fallido'
        DOCUMENT_CREATED = 'DOCUMENT_CREATED', 'Creó concepto de documento'
        VERSION_UPLOADED = 'VERSION_UPLOADED', 'Subió nueva versión'
        VERSION_DOWNLOADED = 'VERSION_DOWNLOADED', 'Descargó versión'
        VERSION_DELETED = 'VERSION_DELETED', 'Eliminó versión'
        VERSION_VERIFIED = 'VERSION_VERIFIED', 'Verificó integridad de versión'
        SALE_CREATED = 'SALE_CREATED', 'Operación comercial iniciada'
        SALE_CONFIRMED = 'SALE_CONFIRMED', 'Operación comercial confirmada'
        INVOICE_GENERATED = 'INVOICE_GENERATED', 'Factura de venta generada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('api.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    username = models.CharField(max_length=150)
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=Action.choices, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Audit Log Entry"
        verbose_name_plural = "Audit Log"
        ordering = ['-timestamp']

class ForensicSecurityLog(models.Model):
    class ThreatLevel(models.TextChoices):
        LOW = 'LOW', 'Baja'
        MEDIUM = 'MEDIUM', 'Media'
        HIGH = 'HIGH', 'Alta'
        CRITICAL = 'CRITICAL', 'Crítica (Amenaza Activa)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey('api.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    threat_level = models.CharField(max_length=20, choices=ThreatLevel.choices, default=ThreatLevel.LOW)
    attack_vector = models.CharField(max_length=100)
    payload_captured = models.JSONField()
    headers_captured = models.JSONField()
    action_taken = models.CharField(max_length=255)
    previous_hash = models.CharField(max_length=64, null=True, blank=True)
    integrity_hash = models.CharField(max_length=64, null=True, blank=True)

    @classmethod
    def log_event(cls, attack_vector, payload, headers, action_taken, threat_level='LOW', user=None, ip=None):
        """
        Registra un evento de seguridad forense con encadenamiento SHA-256.
        """
        last_log = cls.objects.order_by('-timestamp').first()
        prev_hash = last_log.integrity_hash if last_log else "0" * 64

        # Crear instancia sin guardar para calcular hash
        instance = cls(
            source_ip=ip,
            user=user,
            threat_level=threat_level,
            attack_vector=attack_vector,
            payload_captured=payload,
            headers_captured=headers,
            action_taken=action_taken,
            previous_hash=prev_hash
        )

        # Calcular hash de integridad
        data_to_hash = f"{prev_hash}|{attack_vector}|{json.dumps(payload)}|{action_taken}|{timezone.now()}"
        instance.integrity_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
        instance.save()
        return instance

    class Meta:
        ordering = ['-timestamp']

class PublicSystemAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    domain = models.CharField(max_length=50)
    function_name = models.CharField(max_length=100)
    impact_summary = models.TextField()
    compliance_score = models.FloatField(default=1.0)
    is_human_reviewed = models.BooleanField(default=False)
    technical_trace_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

class FraudEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=100)
    score = models.IntegerField()
    ip_address = models.GenericIPAddressField()
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

class SystemAuditLog(models.Model):
    """
    Log de auditoría de sistema inmutable.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=255)
    entity = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.pk:
            raise PermissionError("SystemAuditLog is immutable and cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("SystemAuditLog is immutable and cannot be deleted.")

    class Meta:
        ordering = ['-timestamp']
