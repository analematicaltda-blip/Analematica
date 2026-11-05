from django.db import models
from api.models import CustomUser

class LegacyCustodian(models.Model):
    """
    Representa a un humano responsable de la custodia del legado del sistema.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    appointed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    digital_signature_hash = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return f"CUSTODIO: {self.user.username}"

class LegacyMilestone(models.Model):
    """
    Hitos históricos del sistema registrados para la posteridad.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    integrity_hash = models.CharField(max_length=256)
    evidence_bundle_path = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.timestamp.date()} - {self.title}"

class LegacyGuardrail(models.Model):
    """
    Reglas de legado que no pueden ser modificadas por lógica algorítmica.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    ratified_by = models.ManyToManyField(LegacyCustodian)

    def __str__(self):
        return self.name
