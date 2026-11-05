# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/sargentos/sargento_conciliaciones.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_financieros import (
    SoldadoDescargaExtractos, SoldadoCruceAutomatico,
    SoldadoIdentificadorDiferencias, SoldadoAjustadorContable,
    SoldadoAuditorConciliacion
)

class SargentoConciliaciones(SergeantTemplate):
    """
    NIVEL 5 — SARGENTO DE CONCILIACIONES
    Coordinación de auditoría bancaria y cruce de saldos.
    """
    def _get_soldiers(self):
        return [
            SoldadoDescargaExtractos(sargento=self),
            SoldadoCruceAutomatico(sargento=self),
            SoldadoIdentificadorDiferencias(sargento=self),
            SoldadoAjustadorContable(sargento=self),
            SoldadoAuditorConciliacion(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        common = {"provider_id": params.get("provider_id")}
        return [
            {**common, "type": "EXTRACTOS"},
            {**common, "type": "CRUCE"},
            {**common, "type": "DIFERENCIAS"},
            {**common, "type": "AJUSTE"},
            {**common, "type": "CERTIFICACION"}
        ]
