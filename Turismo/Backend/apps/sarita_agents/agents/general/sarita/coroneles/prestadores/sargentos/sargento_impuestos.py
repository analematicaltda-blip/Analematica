# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/sargentos/sargento_impuestos.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_impuestos import SoldadoCalculoIVA, SoldadoRegistroRetenciones
import logging

logger = logging.getLogger(__name__)

class SargentoImpuestos(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoCalculoIVA(sargento=self),
            SoldadoRegistroRetenciones(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        return [
            {
                "tenant_id": params.get("tenant_id"),
                "base_amount": params.get("base_amount"),
                "document_id": params.get("document_id"),
                "type": "IVA"
            },
            {
                "tenant_id": params.get("tenant_id"),
                "type": "RETENCIONES"
            }
        ]
