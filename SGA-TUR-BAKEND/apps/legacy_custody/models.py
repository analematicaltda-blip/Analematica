from django.db import models
import uuid

class LegacyCustodian(models.Model):
    """
    Representa a los garantes del marco de gobernanza algorítmica.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    entity_represented = models.CharField(max_length=255)
    role = models.CharField(max_length=100, default='GARANTE')
    appointed_at = models.DateTimeField(auto_now_add=True)
    public_key = models.TextField(help_text="Clave pública para validación de ratificaciones multicanal.")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.entity_represented})"

class LegacyMilestone(models.Model):
    """
    Registra hitos históricos de la evolución del sistema para la posteridad.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    justification = models.TextField(help_text="Por qué ocurrió este cambio.")
    timestamp = models.DateTimeField(auto_now_add=True)
    governance_hash = models.CharField(max_length=64, help_text="Hash del estado del sistema al momento del hito.")

    def __str__(self):
        return f"MILESTONE: {self.title} ({self.timestamp.date()})"
