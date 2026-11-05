import uuid
from django.db import models
from django.conf import settings

class GhostSurface(models.Model):
    """
    S-3.1: Superficies Fantasma.
    Endpoints o componentes simulados para atraer y desviar ataques.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    path = models.CharField(max_length=512, help_text="Ruta del endpoint fantasma")
    is_active = models.BooleanField(default=True)
    deception_type = models.CharField(max_length=100, choices=[
        ('FAKE_API', 'API Ficticia'),
        ('HONEYPOT_LOGIN', 'Login Trampa'),
        ('SIMULATED_DB_EXPORT', 'Exportación DB Simulada'),
        ('GHOST_ADMIN_PANEL', 'Panel Admin Fantasma')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.deception_type}: {self.path}"

class AdversarialProfile(models.Model):
    """
    S-3.4: Perfilado Adversarial Avanzado.
    Identifica comportamiento hostil sin necesidad de identidad personal.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_ip = models.GenericIPAddressField(unique=True)
    technical_level = models.CharField(max_length=50, default='UNKNOWN') # SCRIPT_KIDDIE, ADVANCED, BOT
    persistence_score = models.FloatField(default=0.0)
    abandonment_threshold = models.FloatField(default=0.5)

    first_seen = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)

    metadata = models.JSONField(default=dict, blank=True)
    is_quarantined = models.BooleanField(default=False)

    def __str__(self):
        return f"Adversary: {self.source_ip} (Level: {self.technical_level})"

class DeceptionInteractionLog(models.Model):
    """
    S-3.1: Registro de interacciones con las superficies fantasma.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    adversary = models.ForeignKey(AdversarialProfile, on_delete=models.CASCADE, related_name='interactions')
    surface = models.ForeignKey(GhostSurface, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    request_data = models.JSONField()
    response_simulated = models.JSONField()

    cost_cognitive_imposed = models.FloatField(default=1.0, help_text="Estimación del tiempo/esfuerzo desperdiciado por el atacante.")

    class Meta:
        ordering = ['-timestamp']

class DisuasionMetric(models.Model):
    """
    Métricas para el panel de inteligencia defensiva (S-3.6).
    """
    total_dissuaded_attempts = models.IntegerField(default=0)
    avg_abandonment_time_minutes = models.FloatField(default=0.0)
    total_cognitive_cost_imposed = models.FloatField(default=0.0)

    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Métrica de Disuasión"
        verbose_name_plural = "Métricas de Disuasión"
