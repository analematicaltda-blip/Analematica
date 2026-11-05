# backend/apps/sarita_agents/agents/general/sarita/coroneles/contable/sargentos/sargento_asientos.py

from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from ..soldados.soldados_contables import (
    SoldadoRegistroIngreso, SoldadoRegistroGasto,
    SoldadoConciliacionWallet, SoldadoVerificacionFiscal,
    SoldadoCierreParcial
)
import logging

logger = logging.getLogger(__name__)

class SargentoAsientosContables(SergeantTemplate):
    """
    NIVEL 5 — SARGENTO DE ASIENTOS
    Coordinador operativo. Divide el trabajo contable entre sus 5 soldados.
    """
    def _get_soldiers(self):
        return [
            SoldadoRegistroIngreso(sargento=self),
            SoldadoRegistroGasto(sargento=self),
            SoldadoConciliacionWallet(sargento=self),
            SoldadoVerificacionFiscal(sargento=self),
            SoldadoCierreParcial(sargento=self),
        ]

    def plan_microtasks(self, params: dict):
        # Pasar parámetros de persistencia a los soldados si existen
        common = {
            "tenant_id": params.get("tenant_id") or params.get("provider_id"),
            "fecha": params.get("fecha"),
            "user_id": params.get("usuario_id"),
            "movimientos": params.get("movimientos")
        }

        # Lógica de orquestación inteligente del Sargento:
        # Determinar qué microtareas son necesarias según los parámetros.
        tasks = []
        if params.get("movimientos"):
            if params.get("monto_ingreso"):
                tasks.append({**common, "monto": params.get("monto_ingreso"), "type": "INGRESO"})
            else:
                tasks.append({**common, "monto": params.get("monto_gasto", 0), "type": "GASTO"})

        if params.get("reconcile_wallet"):
            tasks.append({**common, "type": "CONCILIACION_WALLET"})

        if params.get("check_fiscal"):
            tasks.append({**common, "type": "FISCAL"})

        if params.get("close_period"):
            tasks.append({**common, "periodo_id": params.get("periodo_id"), "type": "CIERRE"})

        # Fallback si no hay tareas específicas pero se llamó al sargento
        if not tasks:
            tasks.append({**common, "type": "FISCAL"})

        return tasks
