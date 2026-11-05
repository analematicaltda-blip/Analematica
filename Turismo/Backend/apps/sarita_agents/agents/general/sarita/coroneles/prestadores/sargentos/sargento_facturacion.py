# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/sargentos/sargento_facturacion.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_facturacion import (
    SoldadoGeneracionFactura, SoldadoValidacionDIAN, SoldadoNotificacionFactura
)
from ..soldados.soldados_contables import SoldadoRegistroContable
import logging

logger = logging.getLogger(__name__)

class SargentoFacturacion(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoGeneracionFactura(sargento=self),
            SoldadoValidacionDIAN(sargento=self),
            SoldadoNotificacionFactura(sargento=self),
            SoldadoRegistroContable(sargento=self)
        ]

    def plan_microtasks(self, params: dict):
        return [
            {
                "operacion_id": params.get("operacion_id"),
                "type": "GENERACION"
            },
            {
                "factura_id": params.get("factura_id"), # Será llenado post-generación o pasado
                "type": "VALIDACION_DIAN"
            },
            {
                "type": "NOTIFICACION"
            },
            {
                "tenant_id": params.get("tenant_id"),
                "fecha": params.get("fecha"),
                "movimientos": params.get("movimientos"),
                "type": "REGISTRO_CONTABLE"
            }
        ]
