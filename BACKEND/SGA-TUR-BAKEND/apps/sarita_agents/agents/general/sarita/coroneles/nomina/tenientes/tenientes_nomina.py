from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargentos_nomina import (
    SargentoLiquidacion, SargentoPrestaciones, SargentoSeguridadSocial,
    SargentoNovedades, SargentoIndicadores
)
import logging

logger = logging.getLogger(__name__)

class TenienteLiquidacion(TenienteTemplate):
    """ NIVEL 4 — CAPITÁN DE LIQUIDACIÓN """
    def perform_action(self, parametros: dict):
        sargento = SargentoLiquidacion(teniente=self)
        return sargento.handle_order(parametros)

class TenientePrestaciones(TenienteTemplate):
    """ NIVEL 4 — CAPITÁN DE PRESTACIONES """
    def perform_action(self, parametros: dict):
        sargento = SargentoPrestaciones(teniente=self)
        return sargento.handle_order(parametros)

class TenienteSeguridadSocial(TenienteTemplate):
    """ NIVEL 4 — CAPITÁN DE SEGURIDAD SOCIAL """
    def perform_action(self, parametros: dict):
        sargento = SargentoSeguridadSocial(teniente=self)
        return sargento.handle_order(parametros)

class TenienteNovedades(TenienteTemplate):
    """ NIVEL 4 — CAPITÁN DE NOVEDADES """
    def perform_action(self, parametros: dict):
        sargento = SargentoNovedades(teniente=self)
        return sargento.handle_order(parametros)

class TenienteIndicadores(TenienteTemplate):
    """ NIVEL 4 — CAPITÁN DE INDICADORES """
    def perform_action(self, parametros: dict):
        sargento = SargentoIndicadores(teniente=self)
        return sargento.handle_order(parametros)
