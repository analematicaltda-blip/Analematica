from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile

class PeriodoContable(models.Model):
    class Estado(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        CERRADO = 'CERRADO', 'Cerrado'

    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='periodos_contables')
    nombre = models.CharField(max_length=100) # Ej. "Enero 2024"
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ABIERTO)

    class Meta:
        unique_together = ('perfil', 'fecha_inicio', 'fecha_fin')
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.get_estado_display()})"
