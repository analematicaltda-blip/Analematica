from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_nomina import (
    SoldadoLiquidacion, SoldadoPrestaciones, SoldadoSeguridadSocial,
    SoldadoNovedades, SoldadoIndicadores
)

class SargentoLiquidacion(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE LIQUIDACIÓN """
    def _get_soldiers(self):
        return [SoldadoLiquidacion(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "PAYROLL_CALC", "provider_id": params.get("provider_id"), "planilla_id": params.get("planilla_id"), "step": i} for i in range(5)]

class SargentoPrestaciones(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE PRESTACIONES """
    def _get_soldiers(self):
        return [SoldadoPrestaciones(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "BENEFIT_CALC", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]

class SargentoSeguridadSocial(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE SEGURIDAD SOCIAL """
    def _get_soldiers(self):
        return [SoldadoSeguridadSocial(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "SS_CHECK", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]

class SargentoNovedades(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE NOVEDADES """
    def _get_soldiers(self):
        return [SoldadoNovedades(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "NOVELTY_REG", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]

class SargentoIndicadores(SergeantTemplate):
    """ NIVEL 5 — SARGENTO TÉCNICO DE INDICADORES """
    def _get_soldiers(self):
        return [SoldadoIndicadores(sargento=self) for _ in range(5)]
    def plan_microtasks(self, params: dict):
        return [{"type": "HR_METRIC", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]
