from django.db import models
from django.conf import settings
import uuid

class Operator(models.Model):
    """
    Hallazgo 23: App Móvil para Operarios.
    Representa a los trabajadores de campo.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='operator_profile')
    role = models.CharField(max_length=50, choices=[('guia', 'Guía'), ('driver', 'Conductor'), ('operario', 'Operario')])
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='ACTIVE')

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"

class OperatorTracking(models.Model):
    """
    Seguimiento GPS en tiempo real de operarios.
    """
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='tracking_logs')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

class OperationReport(models.Model):
    """
    Reportes de campo (incidencias, fotos, notas).
    """
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    mission_id = models.UUIDField() # ID de la misión asignada
    description = models.TextField()
    image = models.ImageField(upload_to='operation_reports/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
