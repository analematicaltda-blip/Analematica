# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/sargentos/sargento_presupuesto.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_financieros import (
    SoldadoInputMetas, SoldadoTrackingGasto,
    SoldadoAnalistaVarianza, SoldadoValidadorRubros,
    SoldadoAlertaSobrecosto
)

class SargentoPresupuesto(SergeantTemplate):
    """
    NIVEL 5 — SARGENTO DE PRESUPUESTO
    Control de ejecución y alertas presupuestales.
    """
    def _get_soldiers(self):
        return [
            SoldadoInputMetas(sargento=self),
            SoldadoTrackingGasto(sargento=self),
            SoldadoAnalistaVarianza(sargento=self),
            SoldadoValidadorRubros(sargento=self),
            SoldadoAlertaSobrecosto(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        return [{"type": "BUDGET_CONTROL", "provider_id": params.get("provider_id")} for _ in range(5)]
