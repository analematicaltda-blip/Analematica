# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/sargentos/sargento_comercial.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_comerciales import (
    SoldadoRegistroLeadComercial, SoldadoVerificacionLeadComercial,
    SoldadoTrazabilidadVentaComercial, SoldadoIntegracionCRMComercial,
    SoldadoMonitoreoConversionComercial
)
import logging

logger = logging.getLogger(__name__)

class SargentoSeguimientoComercial(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoRegistroLeadComercial(sargento=self),
            SoldadoVerificacionLeadComercial(sargento=self),
            SoldadoTrazabilidadVentaComercial(sargento=self),
            SoldadoIntegracionCRMComercial(sargento=self),
            SoldadoMonitoreoConversionComercial(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        return [
            {"email": params.get("email"), "type": "REGISTRO"},
            {"lead_id": params.get("lead_id"), "type": "VERIFICACION"},
            {"campania": params.get("campania_id"), "type": "TRAZABILIDAD"},
            {"crm": "hubspot", "type": "INTEGRACION"},
            {"day": "today", "type": "MONITOREO"}
        ]
