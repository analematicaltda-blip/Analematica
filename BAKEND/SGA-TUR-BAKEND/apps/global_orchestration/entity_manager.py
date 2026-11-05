import logging
from .models import HoldingEntity, HoldingRegion, HoldingCurrency

logger = logging.getLogger(__name__)

class EntityManager:
    """
    Gestor del ciclo de vida de las empresas del holding (Fase 6).
    """

    @staticmethod
    def create_new_entity(name, code, vertical, region_id, currency_id, **kwargs):
        """
        Lanza una nueva empresa en minutos.
        """
        region = HoldingRegion.objects.get(id=region_id)
        currency = HoldingCurrency.objects.get(id=currency_id)

        entity = HoldingEntity.objects.create(
            name=name,
            code=code,
            vertical=vertical,
            region=region,
            base_currency=currency,
            **kwargs
        )

        logger.info(f"ENTITY_MANAGER: Nueva empresa lanzada: {name} [{vertical}]")
        return entity

    @staticmethod
    def get_entity_metrics_summary(entity_id):
        """
        Consolida métricas básicas de una entidad específica.
        """
        entity = HoldingEntity.objects.get(id=entity_id)
        # Aquí se conectaría con saas_metrics filtrando por tenant_id asociados a esta entidad
        return {
            "entity": entity.name,
            "region": entity.region.name,
            "status": "ACTIVE" if entity.is_active else "INACTIVE"
        }
