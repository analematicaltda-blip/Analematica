# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/sargentos/sargento_obligaciones.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_financieros import (
    SoldadoRegistroCredito, SoldadoCalculadorAmortizacion,
    SoldadoTrackingPagos, SoldadoAnalistaRiesgoCredito,
    SoldadoAuditorDeuda
)

class SargentoObligaciones(SergeantTemplate):
    """
    NIVEL 5 — SARGENTO DE OBLIGACIONES
    Coordinación de créditos y pasivos financieros.
    """
    def _get_soldiers(self):
        return [
            SoldadoRegistroCredito(sargento=self),
            SoldadoCalculadorAmortizacion(sargento=self),
            SoldadoTrackingPagos(sargento=self),
            SoldadoAnalistaRiesgoCredito(sargento=self),
            SoldadoAuditorDeuda(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        common = {
            "provider_id": params.get("provider_id"),
            "sub_task": params.get("sub_task"),
            "data": params.get("data")
        }
        return [common for _ in range(5)]
