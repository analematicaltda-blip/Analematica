# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/sargentos/sargento_contable.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_contables import (
    SoldadoRegistroContable, SoldadoVerificacionContable,
    SoldadoTrazabilidadContable, SoldadoIntegraciónContable,
    SoldadoMonitoreoContable
)
import logging

logger = logging.getLogger(__name__)

class SargentoRegistroContable(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoRegistroContable(sargento=self),
            SoldadoVerificacionContable(sargento=self),
            SoldadoTrazabilidadContable(sargento=self),
            SoldadoIntegraciónContable(sargento=self),
            SoldadoMonitoreoContable(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        # Pasar parámetros de persistencia a los soldados
        common = {
            "tenant_id": params.get("tenant_id") or params.get("provider_id"),
            "fecha": params.get("fecha"),
            "usuario_id": params.get("usuario_id"),
            "movimientos": params.get("movimientos"),
            "descripcion": params.get("descripcion")
        }

        # Divide el trabajo en microtareas según el tipo de soldado
        return [
            {**common, "comprobante_id": params.get("comprobante_id"), "type": "REGISTRO"},
            {**common, "asiento_id": params.get("asiento_id"), "type": "VERIFICACION"},
            {**common, "uuid": params.get("operacion_id"), "type": "TRAZABILIDAD"},
            {**common, "tx_id": params.get("tx_id"), "type": "INTEGRACION"},
            {**common, "metric": "performance", "type": "MONITOREO"}
        ]
