from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_artesanos import (
    SoldadoRegistroInventarioArtesano, SoldadoValidacionPedidoArtesano,
    SoldadoControlStockArtesano, SoldadoConfirmacionDespachoArtesano,
    SoldadoMonitoreoVentasArtesano
)
import logging

logger = logging.getLogger(__name__)

class SargentoGestionTallerArtesano(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoRegistroInventarioArtesano(sargento=self),
            SoldadoValidacionPedidoArtesano(sargento=self),
            SoldadoControlStockArtesano(sargento=self),
            SoldadoConfirmacionDespachoArtesano(sargento=self),
            SoldadoMonitoreoVentasArtesano(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        return [
            {"item": params.get("item"), "type": "INVENTARIO"},
            {"pedido_id": params.get("pedido_id"), "type": "VALIDACION"},
            {"categoria": "barro", "type": "STOCK"},
            {"guia": params.get("guia"), "type": "DESPACHO"},
            {"period": "daily", "type": "MONITOREO"}
        ]
