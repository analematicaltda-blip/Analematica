# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/sargentos/sargento_proyecciones.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_financieros import (
    SoldadoRecoleccionHistorica, SoldadoModeladoEscenarios,
    SoldadoValidacionIA, SoldadoAjusteTendencia,
    SoldadoGeneradorReportePredictivo
)

class SargentoProyecciones(SergeantTemplate):
    """
    NIVEL 5 — SARGENTO DE PROYECCIONES
    Supervisión de escenarios futuros y tendencias de flujo.
    """
    def _get_soldiers(self):
        return [
            SoldadoRecoleccionHistorica(sargento=self),
            SoldadoModeladoEscenarios(sargento=self),
            SoldadoValidacionIA(sargento=self),
            SoldadoAjusteTendencia(sargento=self),
            SoldadoGeneradorReportePredictivo(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        return [{"provider_id": params.get("provider_id")} for _ in range(5)]
