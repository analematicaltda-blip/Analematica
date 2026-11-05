from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel
from apps.prestadores.mi_negocio.gestion_comercial.sales.models import Venta

class Factura(TenantAwareModel):
    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', 'Borrador'
        EMITIDA = 'EMITIDA', 'Emitida'
        ANULADA = 'ANULADA', 'Anulada'

    venta = models.OneToOneField(Venta, on_delete=models.CASCADE, related_name='factura')
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=18, decimal_places=2)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BORRADOR)

    # Datos de control DIAN (Simulados para Fase 2)
    cufe = models.CharField(max_length=255, blank=True, null=True)
    qr_code_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Factura {self.numero_factura} (Venta: {self.venta_id})"

    class Meta(TenantAwareModel.Meta):
        app_label = 'facturacion'
