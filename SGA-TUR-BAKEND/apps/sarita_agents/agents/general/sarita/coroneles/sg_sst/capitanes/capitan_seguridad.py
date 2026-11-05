from apps.sarita_agents.agents.capitan_template import CapitanTemplate
import logging

logger = logging.getLogger(__name__)

class CapitanSeguridad(CapitanTemplate):
    """
    NIVEL 3 — CORONEL DE SEGURIDAD
    Supervisa matriz de riesgos, coordina investigaciones y controla plan anual.
    """
    def _get_tenientes(self) -> dict:
        from ..tenientes.tenientes_especializados import (
            TenienteRiesgos, TenienteIncidentes, TenienteCapacitacion,
            TenienteInspecciones, TenienteIndicadores
        )
        return {
            "riesgos": TenienteRiesgos(),
            "incidentes": TenienteIncidentes(),
            "capacitacion": TenienteCapacitacion(),
            "inspecciones": TenienteInspecciones(),
            "indicadores": TenienteIndicadores(),
        }

    def plan(self, mision):
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        params = mision.directiva_original.get("parameters", {})
        target = params.get("target_area", "riesgos")

        # Mapeo al ID del Teniente en tasks.py
        teniente_id = f"sst_{target}"

        p.pasos_del_plan = {
            "1": {
                "teniente": teniente_id,
                "descripcion": f"Ejecución de tarea de SGSST en área {target}",
                "parametros": params
            }
        }
        p.save()
        return p
