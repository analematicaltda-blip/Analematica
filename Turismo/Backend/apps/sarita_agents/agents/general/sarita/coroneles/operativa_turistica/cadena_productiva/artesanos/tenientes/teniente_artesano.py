from apps.sarita_agents.agents.teniente_template import TenienteTemplate
from ..sargentos.sargento_artesano import SargentoGestionTallerArtesano
from django.utils.module_loading import import_string
BusinessSargentoArtesano = import_string('apps.prestadores.mi_negocio.gestion_operativa.modulos_especializados.artesanos.sargentos.SargentoArtesano')

from api.models import CustomUser
import logging

logger = logging.getLogger(__name__)

class TenienteArtesano(TenienteTemplate):
    def perform_action(self, parametros: dict) -> dict:
        mission_type = parametros.get("mission_type")
        user_id = parametros.get("user_id")

        try:
            user = CustomUser.objects.get(id=user_id) if user_id else None
        except CustomUser.DoesNotExist:
            logger.error(f"TENIENTE ARTESANO: Usuario {user_id} no encontrado.")
            return {"status": "FAILED", "error": f"Usuario {user_id} no encontrado."}

        logger.info(f"TENIENTE ARTESANO: Ejecutando acción '{mission_type}' para usuario {user_id}")

        # 1. Ejecución de Lógica de Negocio Real (Sargento de Negocio)
        business_report = {}
        if mission_type == "REGISTER_PRODUCTION":
            business_report = BusinessSargentoArtesano.actualizar_produccion(parametros, user)
        elif mission_type == "UPDATE_ARTISAN_INVENTORY":
            business_report = BusinessSargentoArtesano.registrar_entrada_inventario(parametros, user)
        elif mission_type == "SYNC_PRODUCTION_CATALOG":
            # Soldado especializado para sincronizar con la Vía Comercial
            from ..soldados.soldados_artesanos import SoldadoSincronizadorComercial
            soldado = SoldadoSincronizadorComercial()
            business_report = soldado.perform_action(parametros)

        # 2. Ejecución de Tareas de IA (Simuladas/Agentes)
        sargento_agente = SargentoGestionTallerArtesano(teniente=self)
        agent_report = sargento_agente.handle_order(parametros)

        return {
            "status": "SUCCESS",
            "message": "Operación de taller artesano procesada integralmente.",
            "business_report": business_report,
            "agent_report": agent_report
        }
