from django.db import models
import uuid
from django.utils import timezone

class SystemicRiskIndicator(models.Model):
    """
    Indicadores de Riesgo Sistémico (Z-PEACE-NET).
    Sensor de estabilidad civilizatoria bajo el Estándar SARITA.
    Capturan señales de tensión en dominios económicos, institucionales o sociales.
    """
    class Domain(models.TextChoices):
        ECONOMIC = 'ECONOMIC', 'Económico'
        INSTITUTIONAL = 'INSTITUTIONAL', 'Institucional'
        SOCIAL = 'SOCIAL', 'Social'
        GOVERNANCE = 'GOVERNANCE', 'Gobernanza'
        ALGORITHMIC = 'ALGORITHMIC', 'Algorítmico'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=20, choices=Domain.choices)
    current_value = models.FloatField()
    baseline_value = models.FloatField()
    threshold_critical = models.FloatField()
    last_update = models.DateTimeField(auto_now=True)

    # Metadatos anonimizados de la fuente
    source_metadata = models.JSONField(default=dict)

    def is_anomalous(self):
        return abs(self.current_value - self.baseline_value) > (self.threshold_critical * 0.5)

    def is_critical(self):
        return abs(self.current_value - self.baseline_value) >= self.threshold_critical

    def __str__(self):
        return f"{self.name} ({self.domain}): {self.current_value}"

class StabilityAlert(models.Model):
    """
    Alertas de Estabilidad Sistémica.
    Generadas cuando uno o varios indicadores entran en fase de anomalía.
    """
    class Severity(models.TextChoices):
        LOW = 'LOW', 'Baja (Detección)'
        MEDIUM = 'MEDIUM', 'Media (Tensión)'
        HIGH = 'HIGH', 'Alta (Inestabilidad)'
        CRITICAL = 'CRITICAL', 'Crítica (Riesgo de Colapso)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now)
    severity = models.CharField(max_length=20, choices=Severity.choices)
    context_summary = models.TextField()
    detected_patterns = models.JSONField(help_text="Patrones detectados por los agentes Tenientes")
    is_active = models.BooleanField(default=True)

    # Vinculación con indicadores
    indicators = models.ManyToManyField(SystemicRiskIndicator, related_name='alerts')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.severity}] Alerta de Estabilidad @ {self.timestamp.date()}"

class MitigationScenario(models.Model):
    """
    Escenarios de Mitigación No Coercitiva.
    Propuestos por agentes Capitanes para desacelerar tensiones.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(StabilityAlert, on_delete=models.CASCADE, related_name='scenarios')
    title = models.CharField(max_length=200)
    description = models.TextField()
    proposed_actions = models.JSONField(help_text="Lista de acciones de alineación institucional")
    estimated_impact = models.TextField()

    # Estatus de la propuesta
    is_validated_by_human = models.BooleanField(default=False)
    is_applied = models.BooleanField(default=False)

    # XAI: Justificación de la ruta
    reasoning_chain = models.JSONField(help_text="Cadena de decisión del agente")

    def __str__(self):
        return f"Escenario: {self.title} (Alerta: {self.alert.id})"
