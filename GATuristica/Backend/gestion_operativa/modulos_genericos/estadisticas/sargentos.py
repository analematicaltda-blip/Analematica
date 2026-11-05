import logging
logger = logging.getLogger(__name__)
class SargentoEstadisticas:
    @staticmethod
    def actualizar_kpi(perfil_id, kpi, valor):
        logger.info(f"SARGENTO: Actualizando KPI {kpi} para {perfil_id}")
