from django.db import models
import uuid

class Lead(models.Model):
    """
    Hallazgo 21: Embudo de ventas automático.
    Almacena leads y su scoring para creación automática de tenants.
    """
    STATUS_CHOICES = [
        ('NEW', 'Nuevo'),
        ('QUALIFIED', 'Calificado'),
        ('TENANT_CREATED', 'Tenant Creado'),
        ('FAILED', 'Fallido'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    company_name = models.CharField(max_length=255)
    source = models.CharField(max_length=100) # landing, ads, etc.
    score = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.company_name} ({self.score})"
