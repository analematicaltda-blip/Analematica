from django.db import models
from django.db.models import Sum
from decimal import Decimal
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
from apps.prestadores.mi_negocio.gestion_comercial.models import FacturaVenta
from apps.prestadores.mi_negocio.gestion_contable.compras.models import FacturaCompra

class Proyecto(models.Model):
    class Estado(models.TextChoices):
        PLANIFICACION = 'PLANIFICACION', 'Planificación'
        EN_CURSO = 'EN_CURSO', 'En Curso'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='proyectos')
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    presupuesto = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PLANIFICACION)

    def __str__(self):
        return self.nombre

    def total_ingresos(self):
        return self.ingresos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    def total_costos(self):
        return self.costos.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

    def rentabilidad(self):
        return self.total_ingresos() - self.total_costos()

class IngresoProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='ingresos')
    factura = models.OneToOneField(FacturaVenta, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    fecha = models.DateField()

    def __str__(self):
        return f"Ingreso de {self.monto} para {self.proyecto.nombre}"

class CostoProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='costos')
    factura_compra = models.OneToOneField(FacturaCompra, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=18, decimal_places=2)
    fecha = models.DateField()

    def __str__(self):
        return f"Costo de {self.monto} para {self.proyecto.nombre}"
