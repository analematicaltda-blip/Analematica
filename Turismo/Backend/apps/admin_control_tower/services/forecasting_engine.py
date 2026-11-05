from decimal import Decimal
from apps.comercial.saas_metrics.revenue_metrics import RevenueMetrics
from apps.comercial.saas_metrics.churn_analysis import ChurnAnalysis

class ForecastingEngine:
    """
    Motor de Proyección Financiera Avanzada (Fase 4).
    """

    @staticmethod
    def project_revenue(months=12, scenario="base"):
        current_mrr = RevenueMetrics.calculate_mrr()
        churn_rate = Decimal(str(ChurnAnalysis.calculate_churn_rate() / 100))

        # Parámetros por escenario
        growth_rates = {
            "conservative": Decimal('0.02'),
            "base": Decimal('0.05'),
            "aggressive": Decimal('0.10')
        }

        growth_rate = growth_rates.get(scenario, growth_rates["base"])

        projections = []
        projected_mrr = current_mrr

        for m in range(1, months + 1):
            # MRR(t) = MRR(t-1) * (1 + growth - churn)
            projected_mrr = projected_mrr * (Decimal('1') + growth_rate - churn_rate)
            projections.append({
                "month": m,
                "mrr": projected_mrr,
                "arr": projected_mrr * 12
            })

        return {
            "scenario": scenario,
            "current_mrr": current_mrr,
            "projections": projections
        }
