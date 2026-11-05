import logging
from decimal import Decimal
from django.db import transaction
from .models import InventoryItem
logger = logging.getLogger(__name__)
class InventarioService:
    @staticmethod
    @transaction.atomic
    def update_stock(item_id, change, tipo_movimiento='AJUSTE', user_id=None, reason="Ajuste Operativo", reference=None):
        """
        Actualiza el stock de un ítem y registra el movimiento.
        Sincronizado con el EventBus para alertas y contabilidad.
        """
        item = InventoryItem.objects.select_for_update().get(id=item_id)
        change_dec = Decimal(str(change))

        # 1. Validación de Disponibilidad (Solo para salidas)
        if change_dec < 0 and item.stock_actual < abs(change_dec):
             raise ValueError(f"Stock Insuficiente para {item.nombre_item}. Disponible: {item.stock_actual}")

        old_qty = item.stock_actual
        item.stock_actual += change_dec
        item.save()

        # 2. Registro del Movimiento
        from .models import MovimientoInventario
        MovimientoInventario.objects.create(
            provider=item.provider,
            item=item,
            tipo_movimiento=tipo_movimiento,
            cantidad=abs(change_dec),
            referencia=reference or reason
        )

        # 3. Emisión de Eventos
        from apps.core_erp.event_bus import EventBus

        # Alerta de Stock Bajo
        if item.stock_actual < item.stock_minimo:
            EventBus.emit(
                "inventory_low",
                {
                    "provider_id": str(item.provider_id),
                    "item_id": str(item.id),
                    "item_name": item.nombre_item,
                    "stock_actual": float(item.stock_actual),
                    "stock_minimo": float(item.stock_minimo)
                },
                severity="warning"
            )

        # Impacto Contable y Omnisciencia
        EventBus.emit(
            "INVENTORY_ADJUSTED",
            {
                "tenant_id": str(item.provider_id),
                "item_id": str(item.id),
                "item_name": item.nombre_item,
                "change": float(change_dec),
                "new_quantity": float(item.stock_actual),
                "reason": reason,
                "reference": reference
            },
            user_id=str(user_id) if user_id else None
        )

        logger.info(f"Inventario actualizado: {item.nombre_item} ({old_qty} -> {item.stock_actual})")
        return item
