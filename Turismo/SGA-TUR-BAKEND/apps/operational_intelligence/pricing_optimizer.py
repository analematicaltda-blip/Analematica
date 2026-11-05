from .models import UnitEconomics
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class PricingOptimizer:
    """
    Analyzes profitability and suggests pricing adjustments.
    """

    @staticmethod
    def get_recommendations():
        low_margin_customers = UnitEconomics.objects.filter(gross_margin__lt=20)
        recommendations = []

        for econ in low_margin_customers:
            recommendations.append({
                'customer_id': str(econ.customer_id),
                'issue': 'Low Gross Margin',
                'current_margin': float(econ.gross_margin),
                'suggestion': 'Upgrade to higher tier or increase per-unit usage price',
                'priority': 'HIGH' if econ.gross_margin < 5 else 'MEDIUM'
            })

        # Logic for plan-wide optimization
        # (Placeholder for complex tier analysis)

        return recommendations
