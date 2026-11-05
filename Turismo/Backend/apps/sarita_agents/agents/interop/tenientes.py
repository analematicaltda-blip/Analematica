import logging
from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from apps.admin_plataforma.services.interoperability_bridge import InteroperabilityBridge
from apps.admin_plataforma.services.quintuple_erp import QuintupleERPService

logger = logging.getLogger(__name__)

class TenienteBridgeInterop(TenienteTemplate):
    def perform_action(self, parametros: dict):
        logger.info("TENIENTE (Bridge): Ejecutando enlace de interoperabilidad.")
        bridge = InteroperabilityBridge(user=self.tarea.plan_tactico.mision.creado_por or self.tarea.plan_tactico.mision.creado_por)
        # Nota: Ajustar obtención de usuario según contexto de misión

        order_id = parametros.get("related_operational_order_id")
        if not order_id:
            raise ValueError("Falta related_operational_order_id para interoperabilidad.")

        service = bridge.link_delivery_to_specialized_order(order_id, parametros)
        return {"delivery_service_id": str(service.id), "status": "LINKED"}

class TenienteImpactoQuintuple(TenienteTemplate):
    def perform_action(self, parametros: dict):
        logger.info("TENIENTE (ERP): Asegurando impacto en 5 dimensiones.")
        erp_service = QuintupleERPService(user=self.tarea.plan_tactico.mision.creado_por)

        event_type = parametros.get("event_type", "INTEROP_ACTION")
        res = erp_service.record_impact(event_type, parametros)
        return {"erp_impact": res}
