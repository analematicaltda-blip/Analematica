from decimal import Decimal
from apps.comercial.saas_metrics.revenue_metrics import RevenueMetrics
from apps.comercial.saas_metrics.churn_analysis import ChurnAnalysis

class InvestorReportingEngine:
    """
    Motor de reportes institucionales para VC/PE (Fase 7).
    """

    @staticmethod
    def get_board_deck_metrics():
        mrr = RevenueMetrics.calculate_mrr()
        churn = ChurnAnalysis.calculate_churn_rate()
        arpu = RevenueMetrics.calculate_arpu()

        # Rule of 40 = Growth Rate + Profit Margin
        growth_rate = 25.0 # Benchmark simulado
        profit_margin = 20.0 # Benchmark simulado

        return {
            "mrr": mrr,
            "arr": mrr * 12,
            "net_churn": churn,
            "arpu": arpu,
            "rule_of_40": growth_rate + profit_margin,
            "burn_rate": Decimal('5000.00'), # Placeholder
            "runway_months": 18, # Placeholder
            "ltv_cac_ratio": 4.5
        }

    @staticmethod
    def generate_quarterly_report():
        return {
            "period": "Q3-2025",
            "summary": "Crecimiento sostenido del 5% intermensual.",
            "metrics": InvestorReportingEngine.get_board_deck_metrics()
        }
