import uuid
from django.db import models
from django.conf import settings

class HistoricalEvent(models.Model):
    """
    Data Lake Institucional: Almacena eventos históricos para análisis de BI y forecasting.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, db_index=True)
    domain = models.CharField(max_length=50)
    payload = models.JSONField()
    timestamp = models.DateTimeField(db_index=True)
    entity_id = models.UUIDField(null=True, blank=True)
    tenant_id = models.CharField(max_length=100, null=True, blank=True)

    # Versionado temporal para auditoría
    version = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Evento Histórico"
        verbose_name_plural = "Data Lake - Eventos"
        ordering = ['-timestamp']

class InstitutionalAuditLog(models.Model):
    """
    Audit Trail Engine: Registro inmutable de cambios críticos con firma digital.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=255)
    impact_financial = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    change_details = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Seguridad
    digital_signature = models.TextField(blank=True, null=True)
    previous_hash = models.CharField(max_length=64, blank=True, null=True)
    integrity_hash = models.CharField(max_length=64, db_index=True)

    class Meta:
        verbose_name = "Log de Auditoría Institucional"
        ordering = ['-timestamp']

class BoardDecision(models.Model):
    """
    Gobernanza Corporativa: Registro de decisiones de la Junta Directiva.
    """
    class Committee(models.TextChoices):
        BOARD = 'BOARD', 'Junta Directiva'
        FINANCE = 'FINANCE', 'Comité Financiero'
        RISK = 'RISK', 'Comité de Riesgo'
        EXPANSION = 'EXPANSION', 'Comité de Expansión'

    class Status(models.TextChoices):
        PROPOSED = 'PROPOSED', 'Propuesta'
        IN_VOTING = 'IN_VOTING', 'En Votación'
        APPROVED = 'APPROVED', 'Aprobada'
        REJECTED = 'REJECTED', 'Rechazada'
        EXECUTED = 'EXECUTED', 'Ejecutada'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    committee = models.CharField(max_length=50, choices=Committee.choices)
    title = models.CharField(max_length=255)
    description = models.TextField()
    proposed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='proposed_decisions')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    impact_simulation = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    finalized_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.committee} - {self.title}"

class ValuationRecord(models.Model):
    """
    Valuation Engine: Seguimiento histórico de la valoración del holding.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(auto_now_add=True, db_index=True)

    valuation_base = models.DecimalField(max_digits=20, decimal_places=2)
    valuation_conservative = models.DecimalField(max_digits=20, decimal_places=2)
    valuation_aggressive = models.DecimalField(max_digits=20, decimal_places=2)

    methodology = models.CharField(max_length=100, default="SaaS Multiples + DCF")
    key_metrics = models.JSONField() # MRR, ARR, Growth, Churn en el momento de la valoración

    class Meta:
        ordering = ['-date']

class DataRoomAccess(models.Model):
    """
    Data Room Automático: Control de accesos a la sala de datos para due diligence.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    requester_name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    purpose = models.TextField()
    authorized_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Access for {self.requester_name} ({self.organization})"
