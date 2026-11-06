# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/sargentos/sargento_inventario.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_inventario import (
    SoldadoAjusteStock, SoldadoValoracionInventario, SoldadoControlPuntoReorden
)
import logging

logger = logging.getLogger(__name__)

class SargentoInventario(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoAjusteStock(sargento=self),
            SoldadoValoracionInventario(sargento=self),
            SoldadoControlPuntoReorden(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        return [
            {
                "item_id": params.get("item_id"),
                "cantidad": params.get("cantidad"),
                "motivo": params.get("motivo"),
                "user_id": params.get("user_id"),
                "type": "AJUSTE"
            },
            {
                "item_id": params.get("item_id"),
                "type": "VALORACION"
            },
            {
                "tenant_id": params.get("tenant_id"),
                "type": "CONTROL_STOCK"
            }
        ]
