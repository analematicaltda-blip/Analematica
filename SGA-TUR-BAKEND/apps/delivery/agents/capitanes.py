import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import PlanTáctico, TareaDelegada

logger = logging.getLogger(__name__)

class CapitanDeliveryBase(CapitanTemplate):
    """ Base síncrona para Delivery (Fase 9) """
    def delegate(self, plan: PlanTáctico):
        logger.info(f"CAPITÁN ({self.__class__.__name__}): Ejecutando plan {plan.id} síncronamente.")
        plan.estado = 'EN_EJECUCION'
        plan.save()

        from .tenientes import (
            TenienteDespacho, TenienteRutas, TenienteRepartidores,
            TenienteSeguimiento, TenienteIndicadores
        )

        roster = {
            "despacho": TenienteDespacho(),
            "rutas": TenienteRutas(),
            "repartidores": TenienteRepartidores(),
            "seguimiento": TenienteSeguimiento(),
            "indicadores": TenienteIndicadores()
        }

        for _, tarea_info in plan.pasos_del_plan.items():
            teniente_key = tarea_info.get("teniente")
            teniente = roster.get(teniente_key)
            if teniente:
                tarea = TareaDelegada.objects.create(
                    plan_tactico=plan,
                    teniente_asignado=teniente_key,
                    descripcion_tarea=tarea_info.get("descripcion", "Tarea de Delivery"),
                    parametros=tarea_info.get("parametros", {}),
                    estado='EN_PROGRESO'
                )
                teniente.execute_task(tarea)

        plan.estado = 'COMPLETADO'
        plan.save()

class CapitanDespacho(CapitanDeliveryBase):
    def _get_tenientes(self) -> dict:
        return {"despacho": "TenienteDespacho"}
    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "1": {"teniente": "despacho", "descripcion": "Gestionar asignación y prioridades de pedidos.", "parametros": mision.directiva_original.get("parameters", {})}
        }
        plan.save()
        return plan

class CapitanRutas(CapitanDeliveryBase):
    def _get_tenientes(self) -> dict:
        return {"rutas": "TenienteRutas"}
    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "1": {"teniente": "rutas", "descripcion": "Optimizar rutas logísticas por zona.", "parametros": mision.directiva_original.get("parameters", {})}
        }
        plan.save()
        return plan

class CapitanRepartidores(CapitanDeliveryBase):
    def _get_tenientes(self) -> dict:
        return {"repartidores": "TenienteRepartidores"}
    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "1": {"teniente": "repartidores", "descripcion": "Control de disponibilidad y flota.", "parametros": mision.directiva_original.get("parameters", {})}
        }
        plan.save()
        return plan

class CapitanSeguimiento(CapitanDeliveryBase):
    def _get_tenientes(self) -> dict:
        return {"seguimiento": "TenienteSeguimiento"}
    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "1": {"teniente": "seguimiento", "descripcion": "Monitorear eventos en tiempo real.", "parametros": mision.directiva_original.get("parameters", {})}
        }
        plan.save()
        return plan

class CapitanIndicadores(CapitanDeliveryBase):
    def _get_tenientes(self) -> dict:
        return {"indicadores": "TenienteIndicadores"}
    def plan(self, mision) -> PlanTáctico:
        plan = self.coronel.get_or_create_plan_tactico(mision, self.__class__.__name__)
        plan.pasos_del_plan = {
            "1": {"teniente": "indicadores", "descripcion": "Generar KPIs logísticos y SLAs.", "parametros": mision.directiva_original.get("parameters", {})}
        }
        plan.save()
        return plan
