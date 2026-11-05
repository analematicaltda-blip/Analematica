import logging
from decimal import Decimal
from .usage_metric_model import UsageMetric

logger = logging.getLogger(__name__)

class RatingEngine:
    """
    Motor de Tasación: Convierte unidades de consumo en montos monetarios.
    """

    @staticmethod
    def calculate_price(metric, quantity):
        """
        Calcula el precio para una cantidad de consumo dada según el modelo de la métrica.
        """
        config = metric.pricing_config
        model = metric.price_model
        quantity = Decimal(str(quantity))

        if model == UsageMetric.PriceModel.FLAT:
            return RatingEngine._calculate_flat(config, quantity)
        elif model == UsageMetric.PriceModel.TIERED:
            return RatingEngine._calculate_tiered(config, quantity)
        elif model == UsageMetric.PriceModel.VOLUME:
            return RatingEngine._calculate_volume(config, quantity)
        elif model == UsageMetric.PriceModel.DYNAMIC:
            return RatingEngine._calculate_dynamic(config, quantity)

        return Decimal('0.00')

    @staticmethod
    def _calculate_flat(config, quantity):
        # Ej: {"price": 100, "threshold": 0}
        price = Decimal(str(config.get('price', 0)))
        threshold = Decimal(str(config.get('threshold', 0)))
        if quantity > threshold:
            return price
        return Decimal('0.00')

    @staticmethod
    def _calculate_tiered(config, quantity):
        # Ej: {"tiers": [{"up_to": 1000, "price": 0.01}, {"up_to": null, "price": 0.008}]}
        tiers = config.get('tiers', [])
        total_amount = Decimal('0.00')
        remaining = quantity
        last_up_to = 0

        for tier in tiers:
            up_to = tier.get('up_to')
            price = Decimal(str(tier.get('price', 0)))

            if up_to is None: # Last tier
                tier_quantity = remaining
            else:
                tier_limit = Decimal(str(up_to)) - last_up_to
                tier_quantity = min(remaining, tier_limit)
                last_up_to = Decimal(str(up_to))

            if tier_quantity > 0:
                total_amount += tier_quantity * price
                remaining -= tier_quantity

            if remaining <= 0:
                break

        return total_amount

    @staticmethod
    def _calculate_volume(config, quantity):
        # Todo el volumen se cobra al precio del tier alcanzado
        tiers = config.get('tiers', [])
        selected_price = Decimal('0.00')

        for tier in tiers:
            up_to = tier.get('up_to')
            price = Decimal(str(tier.get('price', 0)))
            if up_to is None or quantity <= Decimal(str(up_to)):
                selected_price = price
                break

        return quantity * selected_price

    @staticmethod
    def _calculate_dynamic(config, quantity):
        # Basado en costo + margen (ej: IA tokens)
        cost_per_unit = Decimal(str(config.get('base_cost', 0)))
        margin = Decimal(str(config.get('margin_multiplier', 1.2)))
        return quantity * cost_per_unit * margin
