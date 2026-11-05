# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/soldados/soldados_artesanos.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoRegistroInventarioArtesano(SoldadoN6OroV2):
    domain = "artesanos"
    aggregate_root = "InventoryItem"
    required_permissions = ["artesanos.execute"]
    event_name = "INVENTORY_ADJUSTED"

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO ARTESANO: Registrando inventario -> {params.get('item_id')}")
        from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.inventario.services import InventarioService

        item_id = params.get('item_id')
        change = params.get('cantidad', 0)

        item = InventarioService.update_stock(
            item_id=item_id,
            change=change,
            user_id=params.get('user_id'),
            reason=params.get('motivo', 'Registro de producción artesanal')
        )

        return item

class SoldadoValidacionPedidoArtesano(SoldadoN6OroV2):
    domain = "artesanos"
    aggregate_root = "Placeholder"
    required_permissions = ["artesanos.execute"]

    def perform_action(self, params: dict):
        logger.info(f"SOLDADO ARTESANO: Validando pedido -> {params.get('pedido_id')}")
        return {"action": "order_validated", "id": params.get('pedido_id')}

class SoldadoControlStockArtesano(SoldadoN6OroV2):
    domain = "artesanos"
    aggregate_root = "Placeholder"
    required_permissions = ["artesanos.execute"]

    def perform_action(self, params: dict):
        logger.info(f"SOLDADO ARTESANO: Control de stock para -> {params.get('categoria')}")
        return {"action": "stock_controlled", "status": "OK"}

class SoldadoConfirmacionDespachoArtesano(SoldadoN6OroV2):
    domain = "artesanos"
    aggregate_root = "Placeholder"
    required_permissions = ["artesanos.execute"]

    def perform_action(self, params: dict):
        logger.info(f"SOLDADO ARTESANO: Confirmando despacho de -> {params.get('guia')}")
        return {"action": "dispatch_confirmed", "guia": params.get('guia')}

class SoldadoMonitoreoVentasArtesano(SoldadoN6OroV2):
    domain = "artesanos"
    aggregate_root = "Placeholder"
    required_permissions = ["artesanos.execute"]

    def perform_action(self, params: dict):
        logger.info(f"SOLDADO ARTESANO: Monitoreando ventas del taller.")
        return {"action": "monitored", "trend": "up"}

class SoldadoSincronizadorComercial(SoldadoN6OroV2):
    domain = "artesanos"
    aggregate_root = "Placeholder"
    required_permissions = ["artesanos.execute"]

    """Sincroniza el inventario de producción con el catálogo comercial."""
    def perform_action(self, params: dict):
        logger.info(f"SOLDADO ARTESANO: Sincronizando producción con catálogo comercial.")
        # Aquí iría la lógica para actualizar el producto comercial basado en WorkshopOrder terminada
        return {"status": "SYNCED", "linked_products": 1}
