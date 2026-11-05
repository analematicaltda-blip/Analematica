from django.db import models
from django.conf import settings
from decimal import Decimal
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile

class Proveedor(models.Model):
    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='proveedores')
    nombre = models.CharField(max_length=255)
    identificacion = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class FacturaCompra(models.Model):
    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        POR_PAGAR = 'POR_PAGAR', 'Por Pagar'
        PAGADA = 'PAGADA', 'Pagada'
        VENCIDA = 'VENCIDA', 'Vencida'
        ANULADA = 'ANULADA', 'Anulada'

    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='facturas_compra')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name='facturas')
    number = models.CharField(max_length=50)
    issue_date = models.DateField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    impuestos = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.POR_PAGAR)
    notas = models.TextField(blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date']
        unique_together = ('perfil', 'proveedor', 'number')

    def __str__(self):
        return f"Factura {self.number} de {self.proveedor.nombre}"
