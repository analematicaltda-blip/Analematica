from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from ...modulos_genericos.productos_servicios.models import Product

class OrganizadorEvento(models.Model):
    perfil = models.OneToOneField(ProviderProfile, on_delete=models.CASCADE, related_name='organizador_eventos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre

class Evento(models.Model):
    organizador = models.ForeignKey(OrganizadorEvento, on_delete=models.CASCADE, related_name='eventos')
    # Reutilizamos Product para nombre, precio de entrada, etc.
    producto = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='evento')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    ubicacion = models.CharField(max_length=255)
    capacidad = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.producto.nombre

class Promocion(models.Model):
    TIPO_DESCUENTO = [
        ('porcentaje', 'Porcentaje'),
        ('fijo', 'Monto Fijo'),
    ]
    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='promociones')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    tipo_descuento = models.CharField(max_length=10, choices=TIPO_DESCUENTO)
    valor_descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Valor del descuento (ej: 10 para 10% o 5000 para $5000 fijos)"
    )
    # Una promoción puede aplicar a múltiples productos/servicios del proveedor
    productos_aplicables = models.ManyToManyField(Product, related_name='promociones')
    activa = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
