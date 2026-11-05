# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/sargentos/sargento_sst.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_sst import (
    SoldadoRegistroRiesgoSST, SoldadoVerificacionEPPSST,
    SoldadoTrazabilidadIncidenteSST, SoldadoIntegracionNormativaSST,
    SoldadoMonitoreoSaludSST
)
import logging

logger = logging.getLogger(__name__)

class SargentoCoordinacionSST(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoRegistroRiesgoSST(sargento=self),
            SoldadoVerificacionEPPSST(sargento=self),
            SoldadoTrazabilidadIncidenteSST(sargento=self),
            SoldadoIntegracionNormativaSST(sargento=self),
            SoldadoMonitoreoSaludSST(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        return [
            {"riesgo": params.get("riesgo_id"), "type": "REGISTRO"},
            {"epp": True, "type": "VERIFICACION"},
            {"incidente": params.get("incidente_id"), "type": "TRAZABILIDAD"},
            {"norma": "2102", "type": "INTEGRACION"},
            {"emp": params.get("empleado_id"), "type": "MONITOREO"}
        ]
