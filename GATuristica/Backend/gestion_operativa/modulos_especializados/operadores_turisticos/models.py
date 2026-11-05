from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from ...modulos_genericos.productos_servicios.models import Product

class OperadorTuristico(models.Model):
    perfil = models.OneToOneField(ProviderProfile, on_delete=models.CASCADE, related_name='operador_turistico')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    licencia_turismo = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre

class PaqueteTuristico(models.Model):
    operador = models.ForeignKey(OperadorTuristico, on_delete=models.CASCADE, related_name='paquetes', null=True, blank=True)
    # Reutilizamos Product para nombre, precio base, etc.
    producto = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='paquete_turistico', null=True, blank=True)
    duracion_dias = models.PositiveIntegerField()
    incluye = models.TextField(help_text="Breve descripción de lo que incluye el paquete (ej: Alojamiento, Transporte).", blank=True, null=True)

    def __str__(self):
        return self.producto.nombre

class ItinerarioDia(models.Model):
    paquete = models.ForeignKey(PaqueteTuristico, on_delete=models.CASCADE, related_name='itinerario')
    dia = models.PositiveIntegerField()
    titulo = models.CharField(max_length=200, help_text="Ej: 'Día 1: Llegada a la ciudad'")
    descripcion = models.TextField()

    class Meta:
        unique_together = ('paquete', 'dia')
        ordering = ['dia']

    def __str__(self):
        return f"Día {self.dia}: {self.titulo} ({self.paquete.producto.nombre})"
