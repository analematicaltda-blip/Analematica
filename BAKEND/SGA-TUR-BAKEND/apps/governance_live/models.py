from django.db import models
import uuid
from django.utils import timezone

class SystemicState(models.Model):
    """
    Representa el estado operativo global de SARITA (Fase Z-GOVERNANCE-LIVE).
    Implementación del Estándar SARITA para el control de flujo civilizatorio.
    Define el nivel de autonomía y restricción del sistema.
    """
    class StateLevel(models.TextChoices):
        NORMAL = 'NORMAL', 'Estado Normal (Operación Plena)'
        REINFORCED_OBSERVATION = 'OBSERVATION', 'Observación Reforzada'
        PREVENTATIVE_WARNING = 'WARNING', 'Alerta Preventiva'
        CONTAINMENT = 'CONTAINMENT', 'Contención (Restricción de Autonomía)'
        PARTIAL_DECOUPLING = 'PARTIAL_DECOUPLING', 'Desacoplamiento Parcial'
        TOTAL_DECOUPLING = 'TOTAL_DECOUPLING', 'Desacoplamiento Total (Soberanía Pura)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    current_level = models.CharField(
        max_length=50,
        choices=StateLevel.choices,
        default=StateLevel.NORMAL
    )

    timestamp = models.DateTimeField(default=timezone.now)
    authorized_by = models.ForeignKey('api.CustomUser', on_delete=models.PROTECT, related_name='state_authorizations')

    reason = models.TextField(help_text="Justificación institucional del cambio de estado.")
    context_data = models.JSONField(default=dict, help_text="Señales que dispararon la transición.")

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Estado Sistémico"
        verbose_name_plural = "Estados Sistémicos"

    def __str__(self):
        return f"{self.current_level} @ {self.timestamp}"

class GovernanceMemory(models.Model):
    """
    Memoria Institucional (Z-GOVERNANCE-LIVE).
    Componente de Memoria Civilizatoria del Estándar SARITA.
    Almacena patrones históricos de riesgo y respuestas efectivas.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, help_text="Ej: CRISIS_DIPLOMATICA, TENSION_ECONOMICA")
    description = models.TextField()

    # Patrones aprendidos (No ideológicos)
    detected_patterns = models.JSONField(help_text="Indicadores técnicos que precedieron al evento.")
    actions_taken = models.JSONField(help_text="Acciones de gobernanza ejecutadas.")

    effectiveness_score = models.FloatField(default=0.0, help_text="Puntaje de 0 a 1 sobre la efectividad de la respuesta.")
    lessons_learned = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Memoria de Gobernanza"
        verbose_name_plural = "Memorias de Gobernanza"

class CivilizatoryEvent(models.Model):
    """
    FASE META: Records systemic milestones that impact the territory beyond technology.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    impact_level = models.CharField(max_length=50, choices=[('REGIONAL', 'Regional'), ('NATIONAL', 'Nacional'), ('GLOBAL', 'Global')])
    date_occurred = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ['-date_occurred']

    def __str__(self):
        return f"[{self.impact_level}] {self.title}"
