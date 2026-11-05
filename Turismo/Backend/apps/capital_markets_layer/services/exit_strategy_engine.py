from decimal import Decimal
from apps.institutional_layer.services.investor_reporting_engine import InvestorReportingEngine
from .liquidity_scenarios_engine import LiquidityScenariosEngine

class ExitStrategyEngine:
    """
    Motor de Recomendación de Estrategia de Salida (Fase 8).
    Analiza métricas internas para sugerir el mejor camino de liquidez.
    """

    @staticmethod
    def get_exit_recommendation():
        metrics = InvestorReportingEngine.get_board_deck_metrics()
        arr = metrics['arr']
        growth = metrics['rule_of_40'] - 20 # Estimado

        # Lógica estratégica:
        # > $100M ARR + High Growth -> IPO
        # < $50M ARR + High Margin -> Strategic Sale
        # Low Growth + High FCF -> LBO / PE

        if arr > 100000000 and growth > 30:
            recommendation = "IPO_READY"
            reason = "Escala y crecimiento óptimos para mercados públicos."
        elif growth > 40:
            recommendation = "STRATEGIC_SALE"
            reason = "Atractivo alto para adquisidores estratégicos (Adobe/Oracle)."
        else:
            recommendation = "PRIVATE_EQUITY_LBO"
            reason = "Oportunidad de optimización operativa y recapitalización."

        return {
            "primary_recommendation": recommendation,
            "reasoning": reason,
            "timing_suggested": "12-18 months",
            "market_comparables": ["HubSpot", "Salesforce"]
        }
