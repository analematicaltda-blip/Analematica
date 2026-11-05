import uuid
from django.db import models
from django.conf import settings

class PerformanceMetric(models.Model):
    """
    Registra KPIs históricos para análisis de optimización.
    """
    class Domain(models.TextChoices):
        COMERCIAL = 'COMERCIAL', 'Comercial'
        CONTABLE = 'CONTABLE', 'Contable'
        FINANCIERO = 'FINANCIERO', 'Financiero'
        OPERATIVO = 'OPERATIVO', 'Operativo'
        ARCHIVISTICO = 'ARCHIVISTICO', 'Archivístico'
        GOBERNANZA = 'GOBERNANZA', 'Gobernanza'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.CharField(max_length=50, choices=Domain.choices)
    metric_name = models.CharField(max_length=100) # ej: 'ROI', 'TrustLevel', 'ResolutionTime'
    value = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']

class AutonomousAction(models.Model):
    """
    Define una acción que la IA puede ejecutar de forma autónoma.
    Cumple con el punto 2.1 de la Fase F-F.
    """
    class Level(models.IntegerChoices):
        MANUAL = 0, 'Manual'
        ASISTIDA = 1, 'Asistida'
        AUTONOMA_CONDICIONADA = 2, 'Autónoma Condicionada'
        AUTONOMA_SOBERANA = 3, 'Autónoma Soberana (BLOQUEADO)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=50, choices=PerformanceMetric.Domain.choices)
    description = models.TextField()
    autonomy_level = models.IntegerField(choices=Level.choices, default=Level.MANUAL)

    # Límites Hard (Punto 4)
    max_daily_executions = models.IntegerField(default=5)
    max_financial_impact = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    is_active = models.BooleanField(default=True)
    policy_reference = models.CharField(max_length=255, help_text="Referencia a la política legal/técnica")

    def __str__(self):
        return f"{self.name} ({self.domain})"

class AutonomousExecutionLog(models.Model):
    """
    Registro y Auditoría Total de acciones autónomas (Punto 7 y 9).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.ForeignKey(AutonomousAction, on_delete=models.CASCADE, related_name='executions')
    timestamp = models.DateTimeField(auto_now_add=True)

    # XAI (Punto 7)
    explanation = models.TextField(help_text="Explicación en lenguaje humano de por qué se ejecutó.")
    data_points = models.JSONField(help_text="Datos que justificaron la decisión.")
    policy_applied = models.TextField()

    result_status = models.CharField(max_length=50) # 'SUCCESS', 'FAILED', 'BLOCKED_BY_LIMIT', 'KILLED'
    impact_measured = models.JSONField(null=True, blank=True)

    was_interrupted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

class AutonomyControl(models.Model):
    """
    Control soberano de la autonomía (Punto 6).
    """
    class ControlType(models.TextChoices):
        TECHNICAL = 'TECHNICAL', 'Técnico'
        LEGAL = 'LEGAL', 'Legal/Normativo'
        OPERATIVE = 'OPERATIVE', 'Operativo'

    control_type = models.CharField(
        max_length=20,
        choices=ControlType.choices,
        default=ControlType.TECHNICAL
    )
    domain = models.CharField(
        max_length=50,
        choices=PerformanceMetric.Domain.choices,
        unique=True,
        null=True,
        blank=True,
        help_text="Nulo para control Global"
    )
    is_enabled = models.BooleanField(default=True, help_text="Si es Falso, actúa como Kill Switch activado.")
    last_update = models.DateTimeField(auto_now=True)
    reason = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Control: {self.domain or 'GLOBAL'} - {'ACTIVO' if self.is_enabled else 'BLOQUEADO'}"
        indexes = [
            models.Index(fields=['domain', 'metric_name']),
        ]

class OptimizationProposal(models.Model):
    """
    Recomendación del sistema para ajustar parámetros operativos o reglas.
    """
    class Status(models.TextChoices):
        PROPOSED = 'PROPOSED', 'Propuesta'
        APPROVED = 'APPROVED', 'Aprobada'
        REJECTED = 'REJECTED', 'Rechazada'
        EXECUTED = 'EXECUTED', 'Ejecutada'
        REVERTED = 'REVERTED', 'Revertida'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.CharField(max_length=50, choices=PerformanceMetric.Domain.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)

    # --- Contenido de la Optimización ---
    hallazgo = models.TextField(help_text="Patrón detectado que justifica la optimización.")
    propuesta_ajuste = models.TextField(help_text="Descripción técnica del ajuste sugerido.")
    parametros_cambio = models.JSONField(help_text="Valores técnicos a modificar (ej: {'threshold': 0.85}).")
    impacto_esperado = models.TextField()

    # --- Control y Rollback ---
    config_previa = models.JSONField(help_text="Snapshot de la configuración antes del cambio.")
    decidida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    justificacion_admin = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Propuesta de Optimización"
        verbose_name_plural = "Propuestas de Optimización"

class OptimizationAuditLog(models.Model):
    """
    Log especializado de gobernanza para la Fase 6.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(OptimizationProposal, on_delete=models.CASCADE, related_name="audit_logs")
    accion = models.CharField(max_length=50) # ej: 'APPROVE', 'EXECUTE', 'ROLLBACK'
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    detalles = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
