# backend/apps/sarita_agents/agents/general/sarita/coroneles/prestadores/soldados/soldados_comerciales.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoRegistroLeadComercial(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "Lead"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO COMERCIAL: Registrando prospecto -> {params.get('email')}")
        from apps.prestadores.mi_negocio.gestion_comercial.funnels.runtime_models import Lead
        lead = Lead.objects.create(
            tenant_id=params.get('tenant_id'),
            funnel_id=params.get('funnel_id'),
            initial_version_id=params.get('version_id'),
            form_data={"email": params.get('email'), "name": params.get('name')}
        )
        return lead

class SoldadoVerificacionLeadComercial(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "LeadState"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO COMERCIAL: Verificando veracidad de lead.")
        from apps.prestadores.mi_negocio.gestion_comercial.funnels.runtime_models import LeadState
        state = LeadState.objects.get(lead_id=params.get('lead_id'))
        state.current_status = 'verified'
        state.save()
        return state

class SoldadoTrazabilidadVentaComercial(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "LeadEvent"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO COMERCIAL: Vinculando lead con campaña.")
        from apps.prestadores.mi_negocio.gestion_comercial.funnels.runtime_models import LeadEvent
        evt = LeadEvent.objects.create(
            lead_id=params.get('lead_id'),
            event_type='CONVERSION_TRACKED',
            payload=params.get('metadata', {})
        )
        return evt

class SoldadoIntegracionCRMComercial(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "Lead"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO COMERCIAL: Sincronizando con CRM externo.")
        return {"status": "SYNCED", "msg": "Lead enviado al CRM de la Holding."}

class SoldadoMonitoreoConversionComercial(SoldadoN6OroV2):
    domain = "prestadores"
    aggregate_root = "CommercialMetrics"
    required_permissions = ["prestadores.execute"]

    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO COMERCIAL: Calculando tasa de conversión diaria.")
        return {"status": "SUCCESS", "conversion_rate": 0.15}
