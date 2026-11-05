import logging
logger = logging.getLogger(__name__)
class EstadisticaService:
    @staticmethod
    def generate_report(perfil_id, metric_type):
        logger.info(f"Generando reporte {metric_type} para perfil {perfil_id}")
        return {"status": "success"}
