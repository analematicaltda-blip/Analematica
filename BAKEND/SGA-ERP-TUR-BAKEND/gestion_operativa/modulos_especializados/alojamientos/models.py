from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from ...modulos_genericos.productos_servicios.models import Product

# Tipo de Alojamiento (Hotel, Cabaña, Glamping, etc.)
class TipoAlojamiento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# El Alojamiento principal, vinculado al perfil del prestador
class Alojamiento(models.Model):
    perfil = models.OneToOneField(ProviderProfile, on_delete=models.CASCADE, related_name='alojamiento')
    tipo = models.ForeignKey(TipoAlojamiento, on_delete=models.SET_NULL, null=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

# Habitaciones o unidades dentro del Alojamiento
class Habitacion(models.Model):
    alojamiento = models.ForeignKey(Alojamiento, on_delete=models.CASCADE, related_name='habitaciones')
    # Vinculado al Product/Service genérico para reusar campos como nombre, descripción, precio base.
    producto = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='habitacion')
    capacidad_maxima = models.PositiveIntegerField()
    # Podemos añadir más campos específicos como tipo de cama, vistas, etc.

    def __str__(self):
        return f"{self.producto.nombre} en {self.alojamiento.nombre}"

# Tarifas especiales (ej. temporada alta, fin de semana)
class Tarifa(models.Model):
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name='tarifas')
    nombre = models.CharField(max_length=100) # Ej: "Tarifa Fin de Semana", "Temporada Alta"
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    precio_adicional = models.DecimalField(max_digits=10, decimal_places=2, help_text="Valor a sumar (o restar si es negativo) al precio base de la habitación.")

    def __str__(self):
        return f"Tarifa '{self.nombre}' para {self.habitacion.producto.nombre}"
