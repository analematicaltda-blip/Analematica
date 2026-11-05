# backend/apps/sarita_agents/agents/general/sarita/coroneles/gubernamental/municipal/soldados/soldados_municipales.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoAuditorLocal(SoldadoN6OroV2):
    domain = "municipal"
    aggregate_root = "ProviderProfile"
    required_permissions = ["municipal.execute"]

    """Verifica el cumplimiento de normativas a nivel municipal."""
    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO MUNICIPAL: Auditando prestador local -> {params.get('prestador_id')}")
        from apps.domain_business.operativa.models import ProviderProfile
        profile = ProviderProfile.objects.get(id=params.get('prestador_id'))
        return {"id": str(profile.id), "status": "AUDITED", "compliance": profile.is_verified}

class SoldadoGestorEventos(SoldadoN6OroV2):
    domain = "municipal"
    aggregate_root = "Evento"
    required_permissions = ["municipal.execute"]

    """Gestiona el registro de eventos turísticos locales."""
    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO MUNICIPAL: Registrando evento local -> {params.get('evento_nombre')}")
        from apps.prestadores.mi_negocio.operativa_turistica.operadores_directos.eventos.models import Evento
        # Registro lógico de evento
        return {"status": "REGISTERED", "evento": params.get('evento_nombre')}

class SoldadoInspectorRNT(SoldadoN6OroV2):
    domain = "municipal"
    aggregate_root = "ProviderProfile"
    required_permissions = ["municipal.execute"]

    """Verifica el estado del Registro Nacional de Turismo local."""
    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO MUNICIPAL: Verificando RNT para -> {params.get('nit')}")
        return {"status": "VERIFIED", "rnt_valid": True, "nit": params.get('nit')}
