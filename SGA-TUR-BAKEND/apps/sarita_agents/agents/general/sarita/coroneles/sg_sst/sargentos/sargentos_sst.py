from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_sst import (
    SoldadoRiesgos, SoldadoIncidentes, SoldadoCapacitacion,
    SoldadoInspecciones, SoldadoIndicadores
)

class SargentoRiesgos(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE RIESGOS """
    def _get_soldiers(self):
        return [SoldadoRiesgos(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "RISK_EVAL", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]

class SargentoIncidentes(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE INCIDENTES """
    def _get_soldiers(self):
        return [SoldadoIncidentes(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "INCIDENT_REG", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]

class SargentoCapacitacion(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE CAPACITACIÓN """
    def _get_soldiers(self):
        return [SoldadoCapacitacion(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "TRAINING_SST", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]

class SargentoInspecciones(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE INSPECCIONES """
    def _get_soldiers(self):
        return [SoldadoInspecciones(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "INSPECTION_SST", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]

class SargentoIndicadores(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE INDICADORES """
    def _get_soldiers(self):
        return [SoldadoIndicadores(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "METRIC_CALC", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]
