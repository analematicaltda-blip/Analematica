from apps.sarita_agents.agents.capitan_template import CapitanTemplate
import logging

logger = logging.getLogger(__name__)

class CapitanGestionLaboral(CapitanTemplate):
    """
    NIVEL 3 — CORONEL DE GESTIÓN LABORAL
    Supervisa liquidaciones, novedades e integraciones contables.
    """
    def _get_tenientes(self) -> dict:
        from ..tenientes.tenientes_nomina import (
            TenienteLiquidacion, TenientePrestaciones, TenienteSeguridadSocial,
            TenienteNovedades, TenienteIndicadores
        )
        return {
            "liquidacion": TenienteLiquidacion(),
            "prestaciones": TenientePrestaciones(),
            "seguridad_social": TenienteSeguridadSocial(),
            "novedades": TenienteNovedades(),
            "indicadores": TenienteIndicadores(),
        }

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        params = mision.directiva_original.get("parameters", {})
        target = params.get("target_area", "liquidacion")

        # El ID del Teniente para el orquestador
        teniente_id = f"nomina_{target}"

        p.pasos_del_plan = {
            "1": {
                "teniente": teniente_id,
                "descripcion": f"Ejecución de tarea de Nómina en área {target}",
                "parametros": params
            }
        }
        p.save()
        return p
