from django.db import models
import uuid

class IdempotencyKey(models.Model):
    key = models.CharField(max_length=255, db_index=True)
    domain = models.CharField(max_length=100, db_index=True)
    status = models.CharField(max_length=20, default='PENDING') # PENDING, SUCCESS, FAILED
    response_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('key', 'domain')
        app_label = 'sarita_agents'

class OutboxEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, db_index=True)
    domain = models.CharField(max_length=100, db_index=True)
    aggregate_root = models.CharField(max_length=100)
    payload = models.JSONField()
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=20, default='PENDING') # PENDING, PROCESSED, ERROR
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'core_erp'

class SoldadoOperationalStatus(models.Model):
    nombre_soldado = models.CharField(max_length=255, primary_key=True)
    dominio = models.CharField(max_length=100, db_index=True)
    estado = models.CharField(max_length=50, default='Mock') # Mock, Operacional, Certificado
    fecha_certificacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'sarita_agents'
