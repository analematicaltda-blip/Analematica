# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/soldados/soldados_inventario.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoAjusteStock(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "InventoryItem"
    required_permissions = ["prestadores.execute"]
    event_name = "INVENTORY_ADJUSTED"

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO INVENTARIO: Ajustando stock -> {params.get('item_id')}")
        from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.services import InventarioService

        item_id = params.get('item_id')
        change = params.get('cantidad', 0)

        item = InventarioService.update_stock(
            item_id=item_id,
            change=change,
            user_id=params.get('user_id'),
            reason=params.get('motivo', 'Ajuste de inventario vía agente')
        )
        return item

class SoldadoValoracionInventario(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "InventoryItem"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO INVENTARIO: Calculando valoración para {params.get('item_id')}")
        from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.models import InventoryItem
        item = InventoryItem.objects.get(id=params.get('item_id'))
        valor_total = item.cantidad * item.precio_unitario
        return {"id": str(item.id), "valor_total": float(valor_total), "metodo": "PEPS/FIFO"}

class SoldadoControlPuntoReorden(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "InventoryItem"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO INVENTARIO: Verificando punto de reorden.")
        from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.models import InventoryItem

        items_bajo_stock = InventoryItem.objects.filter(
            tenant_id=params.get('tenant_id'),
            cantidad__lte=models.F('punto_reorden')
        )

        return {
            "status": "CHECK_COMPLETE",
            "items_alertados": items_bajo_stock.count()
        }
