from decimal import Decimal
from django.db.models import Sum
from .models import HoldingEntity, HoldingCurrency
from apps.comercial.saas_metrics.revenue_metrics import RevenueMetrics
from .currency_engine import CurrencyEngine

class GlobalConsolidation:
    """
    Motor de Consolidación Global del Holding (Fase 6).
    """

    @staticmethod
    def get_global_revenue():
        """
        Agrega ingresos de todas las empresas del holding convertidos a la moneda base.
        """
        entities = HoldingEntity.objects.filter(is_active=True)
        global_mrr = Decimal('0.00')

        for entity in entities:
            # En una implementación real, cada entidad tendría sus propios tenant_ids vinculados
            # Aquí usamos el RevenueMetrics global como base para el MVP
            entity_mrr = RevenueMetrics.calculate_mrr()

            # Convertimos a moneda del holding
            base_mrr = CurrencyEngine.convert_to_base(entity_mrr, entity.base_currency.code)
            global_mrr += base_mrr

        return {
            "global_mrr": global_mrr,
            "global_arr": global_mrr * 12,
            "entities_count": entities.count()
        }

    @staticmethod
    def revenue_by_region():
        """
        Desglosa ingresos por región geográfica.
        """
        entities = HoldingEntity.objects.filter(is_active=True).select_related('region')
        regional_breakdown = {}

        for entity in entities:
            region_name = entity.region.name
            mrr = RevenueMetrics.calculate_mrr() # Simulado
            base_mrr = CurrencyEngine.convert_to_base(mrr, entity.base_currency.code)

            if region_name not in regional_breakdown:
                regional_breakdown[region_name] = Decimal('0.00')

            regional_breakdown[region_name] += base_mrr

        return regional_breakdown
