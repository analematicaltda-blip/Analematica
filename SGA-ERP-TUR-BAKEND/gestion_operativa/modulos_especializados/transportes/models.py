from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from ...modulos_genericos.productos_servicios.models import Product

class CompaniaTransporte(models.Model):
    perfil = models.OneToOneField(ProviderProfile, on_delete=models.CASCADE, related_name='compania_transporte')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class TipoVehiculo(models.Model):
    nombre = models.CharField(max_length=100, unique=True) # Ej: Bus, Van, Automóvil
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Vehiculo(models.Model):
    compania = models.ForeignKey(CompaniaTransporte, on_delete=models.CASCADE, related_name='vehiculos')
    # Reutilizamos Product para nombre, descripción, precio base por alquiler/pasaje
    producto = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='vehiculo')
    tipo = models.ForeignKey(TipoVehiculo, on_delete=models.SET_NULL, null=True)
    placa = models.CharField(max_length=20, unique=True)
    capacidad_pasajeros = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} ({self.placa})"

class Ruta(models.Model):
    compania = models.ForeignKey(CompaniaTransporte, on_delete=models.CASCADE, related_name='rutas')
    nombre = models.CharField(max_length=200) # Ej: "Ruta del Sol"
    origen = models.CharField(max_length=150)
    destino = models.CharField(max_length=150)
    distancia_km = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre}: {self.origen} - {self.destino}"

class HorarioRuta(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='horarios')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='horarios_asignados')
    hora_salida = models.TimeField()
    hora_llegada_estimada = models.TimeField()
    dias_operacion = models.CharField(max_length=50, help_text="Ej: 'L-V', 'S,D', 'L,M,X'")

    def __str__(self):
        return f"Salida a las {self.hora_salida} en la ruta {self.ruta.nombre}"
