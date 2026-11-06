from decimal import Decimal
import logging
from apps.operational_intelligence.metrics_engine import MetricsEngine
from apps.treasury_automation.cashflow_engine import CashflowEngine

logger = logging.getLogger(__name__)

class CapitalAllocationEngine:
    """
    Decides how to deploy capital for maximum ROI/stability.
    """

    @staticmethod
    def get_allocation_recommendation():
        metrics = MetricsEngine.calculate_all()

        current_cash = CashflowEngine.get_current_balance()
        burn_rate = CashflowEngine.calculate_burn_rate()

        # Strategy logic
        if current_cash < (burn_rate * 6):
            return {
                'strategy': 'CASH_PRESERVATION',
                'recommendation': 'Reduce marketing spend, delay hiring, hold 100% in liquidity.',
                'allocations': {'liquidity': 100, 'growth': 0, 'debt_paydown': 0}
            }

        if metrics.get('churn_rate', 0) > 10:
            return {
                'strategy': 'RETENTION_FOCUS',
                'recommendation': 'Invest in customer success and product stability.',
                'allocations': {'liquidity': 50, 'product': 30, 'marketing': 20}
            }

        return {
            'strategy': 'AGGRESSIVE_GROWTH',
            'recommendation': 'High efficiency detected. Deploy capital into marketing and sales.',
            'allocations': {'marketing': 50, 'liquidity': 20, 'product': 30}
        }
