import uuid
from django.db import models
from django.conf import settings

class ThreatNode(models.Model):
    """
    Representa un componente del sistema que puede ser blanco de ataque o superficie.
    """
    class NodeType(models.TextChoices):
        ENDPOINT = 'ENDPOINT', 'Endpoint de API'
        ROLE = 'ROLE', 'Rol de Usuario'
        AGENT = 'AGENT', 'Agente IA'
        UI_COMPONENT = 'UI_COMPONENT', 'Componente de Interfaz'
        EXTERNAL_SERVICE = 'EXTERNAL_SERVICE', 'Servicio Externo'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    node_type = models.CharField(max_length=50, choices=NodeType.choices)
    risk_score = models.FloatField(default=0.0, help_text="Puntuación de vulnerabilidad actual (0-1).")
    metadata = models.JSONField(default=dict, blank=True)
    is_critical = models.BooleanField(default=False)
    last_observation = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.node_type}] {self.name}"

class ThreatEdge(models.Model):
    """
    Representa la relación o ruta de acceso entre dos nodos.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(ThreatNode, on_delete=models.CASCADE, related_name='outgoing_edges')
    target = models.ForeignKey(ThreatNode, on_delete=models.CASCADE, related_name='incoming_edges')
    edge_type = models.CharField(max_length=100, help_text="Ej: DEPENDS_ON, HAS_ACCESS, AUTH_REQUIRED")
    exposure_level = models.FloatField(default=0.1)

    class Meta:
        unique_together = ('source', 'target', 'edge_type')

class PredictiveScenario(models.Model):
    """
    Simulación adversarial de un posible vector de ataque futuro.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    probability = models.FloatField(help_text="Probabilidad de ocurrencia calculada (0-1).")
    estimated_impact = models.CharField(max_length=100)

    # Grafo del escenario (IDs de nodos afectados)
    affected_nodes = models.JSONField(default=list)
    attack_vector = models.CharField(max_length=100)

    is_active_threat = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-probability']

class PreventiveHardening(models.Model):
    """
    Acción de endurecimiento preventivo aplicada por la IA.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scenario = models.ForeignKey(PredictiveScenario, on_delete=models.CASCADE, related_name='hardening_actions')
    action_name = models.CharField(max_length=255)
    target_node = models.ForeignKey(ThreatNode, on_delete=models.CASCADE)

    # XAI+ (S-2.5)
    explanation = models.TextField()
    estimated_cost_operative = models.FloatField(default=0.0)

    is_applied = models.BooleanField(default=False)
    applied_at = models.DateTimeField(null=True, blank=True)
    expiry_at = models.DateTimeField(help_text="Cuándo revertir automáticamente.")

    config_override = models.JSONField(default=dict)

    def __str__(self):
        return f"PREVENTIVE: {self.action_name} on {self.target_node.name}"


class PDEGovernanceConfig(models.Model):
    """
    S-2.7: Configuración de Gobernanza para el Predictive Defense Engine.
    """
    prediction_threshold = models.FloatField(default=0.7, help_text="Umbral de probabilidad para proponer endurecimiento.")
    is_autonomous_hardening_enabled = models.BooleanField(default=False, help_text="Si es True, la IA aplica medidas L1 sin esperar aprobación.")

    # Ventanas horarias de autonomía (ej: solo de noche)
    start_hour = models.IntegerField(default=0)
    end_hour = models.IntegerField(default=23)

    last_update = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"PDE Governance (Threshold: {self.prediction_threshold})"
