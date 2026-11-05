from django.db import models
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel, ProviderProfile
from apps.prestadores.mi_negocio.gestion_contable.empresa.models import Sucursal
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from django.conf import settings

class Opportunity(TenantAwareModel):
    name = models.CharField(max_length=255)
    # Etapas del pipeline: New, Contacted, Proposal, Negotiation, Won, Lost
    stage = models.CharField(max_length=50, default='New')
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='opportunities')

    def __str__(self):
        return self.name

    class Meta(TenantAwareModel.Meta):
        app_label = 'gestion_comercial'
        verbose_name_plural = "Opportunities"

class Venta(TenantAwareModel):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        CONFIRMADA = 'CONFIRMADA', 'Confirmada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    class MetodoPago(models.TextChoices):
        WALLET = 'WALLET', 'Wallet SARITA'
        EFECTIVO = 'EFECTIVO', 'Efectivo'
        TRANSFERENCIA = 'TRANSFERENCIA', 'Transferencia Bancaria'
        TARJETA = 'TARJETA', 'Tarjeta de Crédito/Débito'

    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT, related_name='ventas')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas', null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    impuestos = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    metodo_pago = models.CharField(max_length=20, choices=MetodoPago.choices, default=MetodoPago.EFECTIVO)

    def __str__(self):
        return f"Venta {self.id} - {self.total}"

    class Meta(TenantAwareModel.Meta):
        app_label = 'gestion_comercial'

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto_ref_id = models.UUIDField(help_text="ID del producto/servicio en el módulo operativo")
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=18, decimal_places=2)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    class Meta:
        app_label = 'gestion_comercial'

class StageHistory(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='stage_history')
    from_stage = models.CharField(max_length=50)
    to_stage = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.opportunity.name}: {self.from_stage} -> {self.to_stage}"
