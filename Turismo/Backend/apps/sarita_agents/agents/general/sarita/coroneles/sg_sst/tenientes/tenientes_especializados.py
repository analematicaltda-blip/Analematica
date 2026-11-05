from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargentos_sst import (
    SargentoRiesgos, SargentoIncidentes, SargentoCapacitacion,
    SargentoInspecciones, SargentoIndicadores
)
import logging

logger = logging.getLogger(__name__)

class TenienteRiesgos(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE RIESGOS
    """
    def perform_action(self, parametros: dict):
        sargento = SargentoRiesgos(teniente=self)
        return sargento.handle_order(parametros)

class TenienteIncidentes(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE INCIDENTES
    """
    def perform_action(self, parametros: dict):
        sargento = SargentoIncidentes(teniente=self)
        return sargento.handle_order(parametros)

class TenienteCapacitacion(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE CAPACITACIÓN
    """
    def perform_action(self, parametros: dict):
        sargento = SargentoCapacitacion(teniente=self)
        return sargento.handle_order(parametros)

class TenienteInspecciones(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE INSPECCIONES
    """
    def perform_action(self, parametros: dict):
        sargento = SargentoInspecciones(teniente=self)
        return sargento.handle_order(parametros)

class TenienteIndicadores(TenienteTemplate):
    """
    NIVEL 4 — CAPITÁN DE INDICADORES
    """
    def perform_action(self, parametros: dict):
        sargento = SargentoIndicadores(teniente=self)
        return sargento.handle_order(parametros)
