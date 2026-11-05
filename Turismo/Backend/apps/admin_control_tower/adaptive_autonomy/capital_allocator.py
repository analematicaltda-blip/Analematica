from decimal import Decimal

class CapitalAllocator:
    """
    Asignador Autónomo de Capital (Fase 5).
    Prioriza inversión basada en salud estructural y crecimiento.
    """

    @staticmethod
    def evaluate_allocation(verticals_data):
        """
        verticals_data: [{name, current_mrr, growth_rate, risk_score}]
        """
        recommendations = []

        for v in verticals_data:
            score = (v['growth_rate'] * 10) - (v['risk_score'] * 5)

            if score > 7.0:
                action = "EXPAND"
                reason = "Alto crecimiento con riesgo controlado."
            elif score < 2.0:
                action = "FREEZE"
                reason = "Bajo rendimiento o riesgo excesivo."
            else:
                action = "MAINTAIN"
                reason = "Estabilidad operativa."

            recommendations.append({
                "vertical": v['name'],
                "score": score,
                "action": action,
                "reason": reason
            })

        return recommendations
