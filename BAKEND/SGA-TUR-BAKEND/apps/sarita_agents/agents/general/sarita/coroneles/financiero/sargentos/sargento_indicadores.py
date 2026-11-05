# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/sargentos/sargento_indicadores.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_financieros import SoldadoKPI

class SargentoIndicadores(SergeantTemplate):
    """
    NIVEL 5 — SARGENTO DE INDICADORES
    Recálculo y auditoría de KPIs de rentabilidad y liquidez.
    """
    def _get_soldiers(self):
        return [SoldadoKPI(sargento=self) for _ in range(5)]

    def plan_microtasks(self, params: dict):
        kpis = ["LIQUIDEZ", "EBITDA", "RENTABILIDAD", "ENDEUDAMIENTO", "ROTACION"]
        return [{"kpi_name": name, "provider_id": params.get("provider_id")} for name in kpis]
