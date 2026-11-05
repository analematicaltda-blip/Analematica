from apps.sarita_agents.agents.sargento_template import SergeantTemplate
from .soldados import (
    SoldadoLogistico
)

class SargentoDeliveryBase(SergeantTemplate):
    def _get_soldiers(self):
        # Cada Sargento tiene exactamente 5 Soldados
        return [SoldadoLogistico(sargento=self, id=i) for i in range(5)]

class SargentoAsignaciones(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "ASSIGN_DRIVER", "order_id": params.get("service_id"), "step": i} for i in range(5)]

class SargentoValidacionInventario(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "CHECK_INV", "order_id": params.get("service_id"), "step": i} for i in range(5)]

class SargentoPrioridades(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "SET_PRIORITY", "order_id": params.get("service_id"), "step": i} for i in range(5)]

class SargentoOptimizacion(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "ROUTE_OPT", "step": i} for i in range(5)]

class SargentoReasignacion(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "REASSIGN", "step": i} for i in range(5)]

class SargentoControlTiempos(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "TIME_TRACK", "step": i} for i in range(5)]

class SargentoFlota(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "FLEET_AUDIT", "step": i} for i in range(5)]

class SargentoIncidentesConductores(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "INCIDENT_LOG", "step": i} for i in range(5)]

class SargentoKPIs(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "CALC_KPI", "provider_id": params.get("provider_id"), "step": i} for i in range(5)]

class SargentoSLAs(SargentoDeliveryBase):
    def plan_microtasks(self, params: dict):
        return [{"micro_action": "CHECK_SLA", "step": i} for i in range(5)]
