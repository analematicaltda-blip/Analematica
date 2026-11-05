# backend/apps/sarita_agents/agents/general/sarita/coroneles/financiero/capitanes/capitan_tesoreria_y_planeacion.py

from apps.sarita_agents.agents.capitan_template import CapitanTemplate
import logging

logger = logging.getLogger(__name__)

class CapitanTesoreriaYPlaneacion(CapitanTemplate):
    """
    NIVEL 3 — CORONEL DE TESORERÍA Y PLANEACIÓN
    Control operativo de flujo, coordinación presupuestal y supervisión de créditos.
    """
    def _get_tenientes(self) -> dict:
        from ..tenientes.teniente_tesoreria import TenienteTesoreria
        from ..tenientes.teniente_presupuestos import TenientePresupuestos
        from ..tenientes.teniente_proyecciones import TenienteProyecciones
        from ..tenientes.teniente_obligaciones import TenienteObligaciones
        from ..tenientes.teniente_indicadores import TenienteIndicadores

        return {
            "tesoreria": TenienteTesoreria(),
            "presupuestos": TenientePresupuestos(),
            "proyecciones": TenienteProyecciones(),
            "obligaciones": TenienteObligaciones(),
            "indicadores": TenienteIndicadores(),
        }

    def plan(self, mision):
        logger.info(f"CORONEL TESORERÍA: Planificando misión {mision.id}")
        p = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)

        # El plan delega según el tipo de directiva
        parameters = mision.directiva_original.get("parameters", {})
        target = parameters.get("target_area", "tesoreria")

        p.pasos_del_plan = {
            "1": {
                "teniente": target,
                "descripcion": f"Ejecución de tarea en el área de {target}.",
                "parametros": parameters
            }
        }
        p.save()
        return p
