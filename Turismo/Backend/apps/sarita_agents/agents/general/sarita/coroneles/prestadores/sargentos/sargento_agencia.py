# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/sargentos/sargento_agencia.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_agencias import (
    SoldadoValidacionReservaAgencia, SoldadoRegistroComisionAgencia,
    SoldadoConfirmacionLiquidacionAgencia, SoldadoVerificacionItinerarioAgencia,
    SoldadoMonitoreoDestinoAgencia
)
import logging

logger = logging.getLogger(__name__)

class SargentoOperativoAgencia(SergeantTemplate):
    def _get_soldiers(self):
        return [
            SoldadoValidacionReservaAgencia(sargento=self),
            SoldadoRegistroComisionAgencia(sargento=self),
            SoldadoConfirmacionLiquidacionAgencia(sargento=self),
            SoldadoVerificacionItinerarioAgencia(sargento=self),
            SoldadoMonitoreoDestinoAgencia(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        return [
            {"reserva_id": params.get("reserva_id"), "type": "RESERVA"},
            {"comision_id": params.get("comision_id"), "type": "COMISION"},
            {"liq_id": params.get("liq_id"), "type": "LIQUIDACION"},
            {"vuelo": params.get("vuelo"), "type": "ITINERARIO"},
            {"dest": params.get("destino"), "type": "DESTINO"}
        ]
