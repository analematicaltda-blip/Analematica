from decimal import Decimal
from apps.comercial.saas_metrics.revenue_metrics import RevenueMetrics

class AcquisitionOptimizer:
    """
    Optimizador de Adquisición (Fase 5).
    Sugiere redistribución de presupuesto basada en eficiencia (LTV/CAC).
    """

    @staticmethod
    def optimize_budget(channels_data):
        """
        channels_data: list of dicts {name, cac, leads_count, conversion_rate}
        """
        ltv = RevenueMetrics.calculate_ltv(churn_rate=5.0) # Simplificado

        optimizations = []
        for channel in channels_data:
            roi_index = float(ltv) / channel['cac'] if channel['cac'] > 0 else 0

            if roi_index > 3.0:
                action = "INCREASE_INVESTMENT"
                recommendation = f"El canal {channel['name']} es altamente eficiente (LTV/CAC > 3)."
            elif roi_index < 1.5:
                action = "REDUCE_INVESTMENT"
                recommendation = f"El canal {channel['name']} tiene baja rentabilidad."
            else:
                action = "MAINTAIN"
                recommendation = "Canal en rango de eficiencia base."

            optimizations.append({
                "channel": channel['name'],
                "roi_index": roi_index,
                "suggested_action": action,
                "reason": recommendation
            })

        return optimizations
