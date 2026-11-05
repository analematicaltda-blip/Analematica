from decimal import Decimal
from apps.comercial.models import Plan
from .reinforcement_engine import ReinforcementEngine

class DynamicPricing:
    """
    Sistema de Pricing Dinámico Controlado (Fase 5).
    """

    @staticmethod
    def suggest_price_adjustment(plan_code, market_demand_index=1.0):
        """
        Sugiere un nuevo precio para un plan basado en demanda y éxito previo.
        market_demand_index: 1.0 neutral, >1.0 alta demanda.
        """
        plan = Plan.objects.filter(code=plan_code, is_active=True).first()
        if not plan:
            return None

        current_price = plan.monthly_price

        # 1. Base por demanda
        suggested = current_price * Decimal(str(market_demand_index))

        # 2. Ajuste por aprendizaje histórico
        adjusted_val = ReinforcementEngine.get_parameter_adjustment(f"PRICE_{plan_code}", float(suggested))
        suggested = Decimal(str(round(adjusted_val, 2)))

        # 3. Reglas de Fairness y Límites (Safety Rails)
        min_price = plan.metadata.get('min_price', current_price * Decimal('0.8'))
        max_price = plan.metadata.get('max_price', current_price * Decimal('1.5'))

        if suggested < min_price:
            suggested = min_price
        elif suggested > max_price:
            suggested = max_price

        return {
            "plan_code": plan_code,
            "current_price": current_price,
            "suggested_price": suggested,
            "variation": ((suggested / current_price) - 1) * 100
        }
