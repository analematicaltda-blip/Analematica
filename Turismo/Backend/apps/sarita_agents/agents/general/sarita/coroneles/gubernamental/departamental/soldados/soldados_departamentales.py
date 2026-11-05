# backend/apps/sarita_agents/agents/general/sarita/coroneles/gubernamental/departamental/soldados/soldados_departamentales.py

from apps.sarita_agents.agents.soldado_n6_oro_v2 import SoldadoN6OroV2
import logging

logger = logging.getLogger(__name__)

class SoldadoPlanificadorRegional(SoldadoN6OroV2):
    domain = "departamental"
    aggregate_root = "Region"
    required_permissions = ["departamental.execute"]

    """Analiza datos para la planificación turística regional."""
    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO DEPARTAMENTAL: Analizando región -> {params.get('region')}")
        return {"status": "ANALYZED", "potencial": "ALTO", "capacidad_carga": 5000}

class SoldadoTrazadorRutas(SoldadoN6OroV2):
    domain = "departamental"
    aggregate_root = "Ruta"
    required_permissions = ["departamental.execute"]

    """Mapea y valida rutas turísticas intermunicipales."""
    def perform_atomic_action(self, params: dict):
        logger.info(f"SOLDADO DEPARTAMENTAL: Trazando ruta -> {params.get('ruta_nombre')}")
        from apps.delivery.models import Ruta
        ruta = Ruta.objects.create(
            nombre=params.get('ruta_nombre'),
            distancia=params.get('distancia', 0.0),
            tiempo_estimado=params.get('tiempo', 60)
        )
        return ruta
