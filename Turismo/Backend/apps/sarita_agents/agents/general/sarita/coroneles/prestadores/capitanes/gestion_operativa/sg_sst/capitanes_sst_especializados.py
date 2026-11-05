import logging
from apps.sarita_agents.agents.capitan_template import CapitanTemplate
from apps.sarita_agents.models import Mision, PlanTáctico

logger = logging.getLogger(__name__)

class CapitanIdentificacionPeligros(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "recorrido_inspeccion", "descripcion": "Realizar inspección para identificar peligros físicos."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanEvaluacionRiesgos(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "matriz_iperc", "descripcion": "Valorar riesgos según probabilidad y consecuencia."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanSaludOcupacional(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "profesiogramas", "descripcion": "Definir perfil de salud por cargo."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanRiesgoPsicosocial(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "bateria_psicosocial", "descripcion": "Aplicar batería de riesgo psicosocial."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanEmergencias(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "plan_evacuacion", "descripcion": "Diseñar o actualizar plan de evacuación."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanCapacitacionSST(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "plan_formacion", "descripcion": "Programar capacitaciones en prevención de riesgos."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}

class CapitanVigilanciaSST(CapitanTemplate):
    def plan(self, mision: Mision) -> PlanTáctico:
        pasos = {"1": {"teniente": "seguimiento_ausentismo", "descripcion": "Analizar indicadores de ausentismo por enfermedad."}}
        return PlanTáctico.objects.create(mision=mision, capitan_responsable=self.__class__.__name__, pasos_del_plan=pasos, estado='PLANIFICADO')
    def _get_tenientes(self) -> dict: return {}
