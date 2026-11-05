# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/sargentos/sargento_finanzas.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_financieros import (
    SoldadoTesorero, SoldadoAnalistaPresupuesto,
    SoldadoAnalistaCredito, SoldadoAuditorFinanciero,
    SoldadoEspecialistaProyecciones
)

class SargentoFinanzas(SergeantTemplate):
    """
    NIVEL 5 — SARGENTO DE FINANZAS
    Coordinador operativo del departamento financiero.
    """
    def _get_soldiers(self):
        return [
            SoldadoTesorero(sargento=self),
            SoldadoAnalistaPresupuesto(sargento=self),
            SoldadoAnalistaCredito(sargento=self),
            SoldadoAuditorFinanciero(sargento=self),
            SoldadoEspecialistaProyecciones(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        common = {
            "provider_id": params.get("provider_id"),
            "usuario_id": params.get("usuario_id"),
        }
        return [
            {**common, "type": "TESORERIA"},
            {**common, "type": "PRESUPUESTO"},
            {**common, "type": "CREDITO"},
            {**common, "type": "AUDITORIA"},
            {**common, "type": "PROYECCION"}
        ]
