from django.db import models
from django.utils.translation import gettext_lazy as _
from ..perfil.models import TenantAwareModel

class InventoryItem(TenantAwareModel):
    """
    Modelo para gestionar el inventario de consumibles de un prestador.
    Adaptado para la nueva arquitectura.
    """
    class ItemType(models.TextChoices):
        CONSUMABLE = 'CONSUMABLE', _('Consumible')
        ASSET = 'ASSET', _('Activo Fijo')
        RETAIL = 'RETAIL', _('Producto de Venta')

    nombre_item = models.CharField(_("Nombre del Ítem"), max_length=255)
    item_type = models.CharField(_("Tipo de Ítem"), max_length=20, choices=ItemType.choices, default=ItemType.CONSUMABLE)

    stock_actual = models.DecimalField(_("Stock Actual"), max_digits=10, decimal_places=2, default=0.00)
    stock_minimo = models.DecimalField(_("Stock Mínimo"), max_digits=10, decimal_places=2, default=0.00)
    stock_maximo = models.DecimalField(_("Stock Máximo"), max_digits=10, decimal_places=2, default=0.00)

    unidad = models.CharField(_("Unidad de Medida"), max_length=50, help_text=_("Ej: unidades, kg, litros"))
    punto_reorden = models.DecimalField(_("Punto de Reorden"), max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.nombre_item} ({self.stock_actual} {self.unidad})"

    class Meta(TenantAwareModel.Meta):
        verbose_name = "Ítem de Inventario"
        verbose_name_plural = "Ítems de Inventario"
        ordering = ['nombre_item']
        app_label = 'prestadores'

class MovimientoInventario(TenantAwareModel):
    class TipoMovimiento(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'
        AJUSTE = 'AJUSTE', 'Ajuste'
        VENTA = 'VENTA', 'Venta'
        COMPRA = 'COMPRA', 'Compra'

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=20, choices=TipoMovimiento.choices)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    referencia = models.CharField(max_length=255, blank=True, null=True, help_text="Referencia a Venta ID o Factura ID")

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.item.nombre_item} ({self.cantidad})"

    class Meta(TenantAwareModel.Meta):
        app_label = 'prestadores'

class AsignacionRecurso(models.Model):
    """Vínculo entre un recurso de inventario y una orden operativa."""
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='asignaciones')
    orden_operativa_ref_id = models.UUIDField()
    cantidad_asignada = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_consumida_real = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)

    class Meta:
        app_label = 'prestadores'
