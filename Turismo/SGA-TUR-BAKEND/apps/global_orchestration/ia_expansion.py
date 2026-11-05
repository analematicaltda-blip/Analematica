from decimal import Decimal
from apps.admin_control_tower.services.forecasting_engine import ForecastingEngine

class IAExpansionGuide:
    """
    Detector de potencial de expansión internacional basado en datos (Fase 6).
    """

    @staticmethod
    def evaluate_market_entry(country_code, target_leads_count):
        """
        Simula la entrada a un nuevo mercado.
        """
        # Obtenemos benchmark global
        projections = ForecastingEngine.project_revenue(months=12)
        avg_mrr_per_tenant = Decimal('150.00') # Benchmark

        expected_mrr = Decimal(str(target_leads_count)) * Decimal('0.10') * avg_mrr_per_tenant # 10% conv

        # Análisis de riesgo regulatorio/fiscal (simulado)
        risk_factor = 1.1 if country_code in ['BR', 'AR'] else 1.0

        return {
            "market": country_code,
            "expected_mrr_12m": expected_mrr * 12,
            "estimated_cac": Decimal('500.00') * risk_factor,
            "ltv_proyectado": expected_mrr * 24,
            "recommendation": "HIGH_POTENTIAL" if expected_mrr > 5000 else "MONITOR"
        }
