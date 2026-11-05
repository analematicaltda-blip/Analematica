# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/sargentos/sargento_cartera.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_cartera import SoldadoSeguimientoCartera, SoldadoGestionCobro
import logging

logger = logging.getLogger(__name__)

class SargentoCartera(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoSeguimientoCartera(sargento=self),
            SoldadoGestionCobro(sargento=self)
        ]

    def plan_microtasks(self, params: dict):
        return [
            {
                "tenant_id": params.get("tenant_id"),
                "type": "SEGUIMIENTO"
            },
            {
                "tenant_id": params.get("tenant_id"),
                "type": "COBRO"
            }
        ]
