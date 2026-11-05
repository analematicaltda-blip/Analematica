
import uuid
from django.db import models
from django.conf import settings
from apps.domain_business.operativa.models import ProviderProfile

class AgentInteraction(models.Model):
    """
    Registro persistente de mensajes del PCA.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    correlation_id = models.UUIDField(db_index=True)
    sender_id = models.CharField(max_length=100)
    interaction_type = models.CharField(max_length=50)
    payload = models.JSONField()
    intelligence = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'admin_plataforma'

class DecisionHistory(models.Model):
    """
    Memoria Contextual y Estratégica: Almacena el resultado histórico de decisiones.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    intention = models.CharField(max_length=255, db_index=True)
    input_params = models.JSONField()
    risk_score = models.FloatField()
    consensus_score = models.FloatField()
    final_status = models.CharField(max_length=50, db_index=True)
    execution_time_ms = models.IntegerField(null=True, blank=True)
    was_compensated = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    embedding = models.BinaryField(null=True, blank=True, help_text="Representación vectorial de la decisión.")

    class Meta:
        app_label = 'admin_plataforma'

class AgentPerformance(models.Model):
    """
    Métricas de rendimiento de agentes para ajuste dinámico de pesos.
    """
    agent_id = models.CharField(max_length=100, primary_key=True)
    total_votes = models.IntegerField(default=0)
    votes_in_consensus = models.IntegerField(default=0, help_text="Veces que votó con la decisión final exitosa.")
    avg_confidence = models.FloatField(default=0.0)
    current_weight_multiplier = models.FloatField(default=1.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'admin_plataforma'

class AdaptiveProposal(models.Model):
    """
    Propuestas generadas por el motor de inteligencia para optimizar el sistema.
    """
    TYPE_CHOICES = [
        ('WEIGHT_ADJUST', 'Ajuste de Pesos PCA'),
        ('WORKFLOW_OPT', 'Optimización de Workflow'),
        ('RISK_THRESHOLD', 'Ajuste de Umbral de Riesgo'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    proposal_data = models.JSONField()
    reasoning = models.TextField()
    is_applied = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'admin_plataforma'

class WorkflowDefinition(models.Model):
    """
    Define la estructura y pasos de un proceso automatizado.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    definition = models.JSONField(help_text="Esquema JSON con pasos, dependencias y compensaciones.")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'admin_plataforma'
        unique_together = ('name', 'version')

    def __str__(self):
        return f"{self.name} (v{self.version})"

class WorkflowInstance(models.Model):
    """
    Representa una ejecución única de un workflow.
    """
    class State(models.TextChoices):
        CREATED = 'CREATED', 'Created'
        RUNNING = 'RUNNING', 'Running'
        WAITING = 'WAITING', 'Waiting'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        COMPENSATING = 'COMPENSATING', 'Compensating'
        ROLLED_BACK = 'ROLLED_BACK', 'Rolled Back'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    definition = models.ForeignKey(WorkflowDefinition, on_delete=models.PROTECT)
    correlation_id = models.UUIDField(db_index=True, help_text="ID del comando MCP que disparó esto.")
    status = models.CharField(max_length=20, choices=State.choices, default=State.CREATED, db_index=True)
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    current_step_index = models.IntegerField(default=0)

    class Meta:
        app_label = 'admin_plataforma'

class StepExecution(models.Model):
    """
    Registro de la ejecución de un paso individual dentro de un workflow.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instance = models.ForeignKey(WorkflowInstance, on_delete=models.CASCADE, related_name="steps")
    step_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='PENDING')
    attempts = models.IntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)
    is_compensated = models.BooleanField(default=False)

    class Meta:
        app_label = 'admin_plataforma'

class GovernanceAuditLog(models.Model):
    """
    Registro unificado de auditoría para el núcleo de gobernanza (MCP).
    Almacena cada intención procesada por el kernel.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="governance_logs"
    )
    intencion = models.CharField(max_length=255, db_index=True)
    parametros = models.JSONField(default=dict)
    resultado = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)
    es_intervencion_soberana = models.BooleanField(default=False)

    # --- Hardening Técnico (RC-S): Integridad de Auditoría ---
    integrity_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    previous_hash = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        app_label = 'admin_plataforma'
        ordering = ['-timestamp']

class GovernancePolicy(models.Model):
    """
    Define reglas globales de gobernanza que condicionan la operación del sistema.
    Permite al Super Admin establecer bloqueos, umbrales y requisitos transversales.
    """
    TYPE_CHOICES = [
        ('BLOCK', 'Bloqueo Total'),
        ('THRESHOLD', 'Umbral de Alerta/Bloqueo'),
        ('REQUIRE_VERIFICATION', 'Requiere Verificación Manual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    domain = models.CharField(max_length=100, default='global', help_text="Dominio afectado (global, comercial, etc.)")
    affected_intentions = models.JSONField(default=list, help_text="Lista de intenciones que responden a esta política.")
    config = models.JSONField(default=dict, help_text="Configuración dinámica (ej: {'limit': 1000})")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'admin_plataforma'
        verbose_name = "Política de Gobernanza"
        verbose_name_plural = "Políticas de Gobernanza"

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class GovernanceIntention(models.Model):
    """
    Formal lifecycle record for any high-level business intention.
    Used for predictive validation and auditable execution.
    """
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Received'
        VALIDATING = 'VALIDATING', 'Validating'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        EXECUTING = 'EXECUTING', 'Executing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    origin_domain = models.CharField(max_length=100)
    trigger_event = models.CharField(max_length=100)
    requested_action = models.JSONField()

    risk_score = models.FloatField(default=0.0)
    validation_status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)

    execution_result = models.JSONField(null=True, blank=True)
    hash_chain = models.CharField(max_length=64, null=True, blank=True, db_index=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_plataforma'

class GovernancePolicyVersion(models.Model):
    """
    Versioning for Governance policies to allow rollbacks and audit of regulatory changes.
    """
    policy = models.ForeignKey(GovernancePolicy, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    config_snapshot = models.JSONField()

    reason_for_change = models.TextField()
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'admin_plataforma'
        unique_together = ('policy', 'version_number')


class PlatformGlobalSettings(models.Model):
    """
    Configuraciones maestras de la plataforma SARITA, accesibles solo por el Super Admin.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Comisiones
    social_gift_commission_pct = models.DecimalField(max_digits=5, decimal_places=2, default=2.00, help_text="Porcentaje de comisión por regalos sociales.")
    room_entry_commission_pct = models.DecimalField(max_digits=5, decimal_places=2, default=10.00, help_text="Porcentaje de comisión por entrada a salas privadas.")

    # Límites
    max_gift_amount = models.DecimalField(max_digits=12, decimal_places=2, default=100000.00)

    # Flags de Sistema
    maintenance_mode = models.BooleanField(default=False)
    registration_open = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'admin_plataforma'
        verbose_name = "Configuración Global de Plataforma"

    def __str__(self):
        return "Configuración Maestra SARITA"
