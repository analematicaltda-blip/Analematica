import uuid
from django.db import models
from django.conf import settings

class StrategyProposal(models.Model):
    """
    Representa una recomendación estratégica generada por un Agente Decisor.
    """
    class Domain(models.TextChoices):
        FINANCIERO = 'FINANCIERO', 'Financiero'
        OPERATIVO = 'OPERATIVO', 'Operativo'
        COMERCIAL = 'COMERCIAL', 'Comercial'
        NORMATIVO = 'NORMATIVO', 'Normativo'
        SISTEMICO = 'SISTEMICO', 'Sistémico'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente de Revisión'
        APPROVED = 'APPROVED', 'Aprobada'
        REJECTED = 'REJECTED', 'Rechazada'
        POSTPONED = 'POSTPONED', 'Postergada'
        EXECUTED = 'EXECUTED', 'Ejecutada'
        FAILED = 'FAILED', 'Fallo en Ejecución'

    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Bajo Riesgo'
        MEDIUM = 'MEDIUM', 'Medio Riesgo'
        HIGH = 'HIGH', 'Alto Riesgo'

    class DecisionLevel(models.IntegerChoices):
        LEVEL_1 = 1, 'Automática (Riesgo Bajo, Reversible)'
        LEVEL_2 = 2, 'Supervisada (Riesgo Medio, Espera Confirmación)'
        LEVEL_3 = 3, 'Estratégica (Alto Impacto, Recomendación)'

    class UrgencyLevel(models.TextChoices):
        LOW = 'LOW', 'Baja'
        MEDIUM = 'MEDIUM', 'Media'
        HIGH = 'HIGH', 'Alta'
        CRITICAL = 'CRITICAL', 'Crítica'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    domain = models.CharField(max_length=50, choices=Domain.choices)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.PENDING)

    # --- Estructura Obligatoria de la Propuesta ---
    contexto_detectado = models.TextField(help_text="Contexto histórico y patrones detectados.")
    riesgo_actual = models.TextField(help_text="Evaluación del riesgo si no se actúa.")
    oportunidad_detectada = models.TextField(help_text="Beneficio potencial de la acción.")
    accion_sugerida = models.JSONField(help_text="Directiva técnica sugerida (Intención + Parámetros).")
    impacto_estimado = models.TextField(help_text="Proyección de resultados.")

    nivel_confianza = models.FloatField(default=0.0, help_text="Probabilidad de éxito estimada por la IA (0-1).")
    nivel_urgencia = models.CharField(max_length=20, choices=UrgencyLevel.choices, default=UrgencyLevel.LOW)
    nivel_riesgo = models.CharField(max_length=20, choices=RiskLevel.choices, default=RiskLevel.LOW)
    decision_level = models.IntegerField(choices=DecisionLevel.choices, default=DecisionLevel.LEVEL_3)

    # --- Trazabilidad ---
    agent_id = models.CharField(max_length=255, help_text="Identificador del agente que generó la propuesta.")
    agent_id_type = models.CharField(max_length=50, blank=True, null=True)
    decidida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decisiones_estrategicas"
    )
    justificacion_humana = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Propuesta Estratégica"
        verbose_name_plural = "Propuestas Estratégicas"
        ordering = ['-created_at']

    def __str__(self):
        return f"Propuesta {self.domain} - {self.get_status_display()} ({self.created_at.date()})"

class DecisionMatrix(models.Model):
    """
    Matriz de Autorización configurable por el Super Admin.
    Define qué tipos de riesgo requieren intervención humana.
    """
    risk_level = models.CharField(max_length=20, choices=StrategyProposal.RiskLevel.choices, unique=True)
    requires_approval = models.BooleanField(default=True, help_text="Si es False, se permite ejecución autónoma bajo regla previa.")
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Matriz de Decisión"
        verbose_name_plural = "Matrices de Decisión"

    def __str__(self):
        return f"Política de Riesgo: {self.risk_level}"
