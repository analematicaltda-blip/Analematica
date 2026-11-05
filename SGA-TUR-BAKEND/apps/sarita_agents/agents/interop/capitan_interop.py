import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico, TareaDelegada

logger = logging.getLogger(__name__)

class CapitanInteroperabilidad(CapitanTemplate):
    """
    Capitán de Interoperabilidad: Coordina misiones que cruzan dominios (Operativo <-> Logístico <-> ERP).
    """

    def delegate(self, plan: PlanTáctico):
        logger.info(f"CAPITÁN (Interoperabilidad): Ejecutando misión interoperable {plan.mision.id} (SÍNCRONA)")
        plan.estado = 'EN_EJECUCION'
        plan.save()

        from .tenientes import TenienteBridgeInterop, TenienteImpactoQuintuple
        from apps.delivery.agents.tenientes import TenienteValidacionServicio

        roster = {
            "validacion_servicio": TenienteValidacionServicio(),
            "bridge_interop": TenienteBridgeInterop(),
            "impacto_quintuple": TenienteImpactoQuintuple()
        }

        for _, tarea_info in plan.pasos_del_plan.items():
            teniente_name = tarea_info.get("teniente")
            teniente = roster.get(teniente_name)
            if teniente:
                tarea = TareaDelegada.objects.create(
                    plan_tactico=plan,
                    teniente_asignado=teniente_name,
                    descripcion_tarea=tarea_info.get("descripcion", "N/A"),
                    parametros=tarea_info.get("parametros", {}),
                    estado='EN_PROGRESO'
                )
                teniente.execute_task(tarea)

        plan.estado = 'COMPLETADO'
        plan.save()

    def plan(self, mision) -> PlanTáctico:
        pasos = {
            "paso_1": {
                "teniente": "bridge_interop",
                "descripcion": "Vincular orden operativa con logística delivery",
                "parametros": mision.directiva_original.get("parameters", {})
            },
            "paso_2": {
                "teniente": "impacto_quintuple",
                "descripcion": "Propagar impacto a las 5 dimensiones del ERP",
                "parametros": mision.directiva_original.get("parameters", {})
            }
        }
        return PlanTáctico.objects.create(
            mision=mision,
            capitan_responsable=self.__class__.__name__,
            pasos_del_plan=pasos,
            estado='PLANIFICADO'
        )

    def _get_tenientes(self) -> dict:
        return {
            "bridge_interop": "TenienteBridgeInterop",
            "impacto_quintuple": "TenienteImpactoQuintuple"
        }
