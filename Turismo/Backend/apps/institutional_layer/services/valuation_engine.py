from decimal import Decimal
from apps.comercial.saas_metrics.revenue_metrics import RevenueMetrics
from .investor_reporting_engine import InvestorReportingEngine

class ValuationEngine:
    """
    Motor de valoración financiera en tiempo real (Fase 7).
    """

    @staticmethod
    def calculate_valuation():
        metrics = InvestorReportingEngine.get_board_deck_metrics()
        arr = metrics['arr']

        # Múltiplos según Rule of 40 (Benchmark SaaS)
        # Rule of 40 > 40% -> Multiplier 10x
        # Rule of 40 < 40% -> Multiplier 6x
        multiplier_base = Decimal('10.0') if metrics['rule_of_40'] >= 40 else Decimal('6.0')

        val_base = arr * multiplier_base

        return {
            "valuation_base": val_base,
            "valuation_conservative": val_base * Decimal('0.8'),
            "valuation_aggressive": val_base * Decimal('1.4'),
            "multiplier_applied": float(multiplier_base),
            "methodology": "Rule of 40 Weighted Multiple"
        }

    @staticmethod
    def simulate_valuation_impact(growth_delta, churn_delta):
        """
        Simula cómo cambia el valor del holding ante variaciones en métricas.
        """
        current_val = ValuationEngine.calculate_valuation()
        # Lógica de simulación de impacto...
        return current_val
