from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import ProviderProfile
# Apuntar al modelo de Producto unificado en gestion_operativa
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product as ProductoUnificado

from apps.core_erp.base.base_models import BaseWarehouse, BaseInventoryMovement

class Almacen(BaseWarehouse):
    perfil = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='almacenes')

    def __str__(self):
        return self.name

class MovimientoInventario(BaseInventoryMovement):
    class TipoMovimiento(models.TextChoices):
        ENTRADA = 'ENTRADA', 'Entrada'
        SALIDA = 'SALIDA', 'Salida'
        AJUSTE_POSITIVO = 'AJUSTE_POSITIVO', 'Ajuste Positivo'
        AJUSTE_NEGATIVO = 'AJUSTE_NEGATIVO', 'Ajuste Negativo'

    # Se cambia la FK para apuntar al modelo de producto unificado
    producto = models.ForeignKey(ProductoUnificado, on_delete=models.CASCADE, related_name='movimientos_inventario')
    almacen = models.ForeignKey(Almacen, on_delete=models.PROTECT, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=20, choices=TipoMovimiento.choices)
    description = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.tipo_movimiento} de {self.cantidad} para {self.producto.nombre}"

    def save(self, *args, **kwargs):
        # La lógica de actualizar el stock total ahora reside en el producto unificado
        # o en una capa de servicio. Este modelo solo registra el movimiento.
        # NOTA: La validación de stock suficiente debería ocurrir en la capa de servicio/vista
        # antes de crear el movimiento.
        super().save(*args, **kwargs)
