# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/sargentos/sargento_tesoreria.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_tesoreria import (
    SoldadoRegistroEfectivo, SoldadoVerificadorBancario,
    SoldadoConciliadorMicro, SoldadoValidadorOperativo,
    SoldadoActualizadorSaldos
)

class SargentoTesoreria(SergeantTemplate):
    """
    NIVEL 5 — SARGENTO DE TESORERÍA
    Coordina la ejecución manual y verificación de flujos de caja.
    """
    def _get_soldiers(self):
        return [
            SoldadoRegistroEfectivo(sargento=self),
            SoldadoVerificadorBancario(sargento=self),
            SoldadoConciliadorMicro(sargento=self),
            SoldadoValidadorOperativo(sargento=self),
            SoldadoActualizadorSaldos(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        common = {
            "provider_id": params.get("provider_id"),
            "usuario_id": params.get("usuario_id"),
        }
        return [
            {**common, "type": "REGISTRO", "desc": "Registro de movimientos manuales"},
            {**common, "type": "VERIFICACION", "desc": "Verificación de soportes"},
            {**common, "type": "CONCILIACION", "desc": "Conciliación de saldos micro"},
            {**common, "type": "VALIDACION", "desc": "Validación de integridad"},
            {**common, "type": "ACTUALIZACION", "desc": "Sincronización de saldos finales"}
        ]
