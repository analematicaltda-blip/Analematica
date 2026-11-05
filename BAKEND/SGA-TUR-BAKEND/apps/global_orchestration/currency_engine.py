from decimal import Decimal
from .models import HoldingCurrency

class CurrencyEngine:
    """
    Motor de conversión y análisis cambiario (Fase 6).
    """

    @staticmethod
    def convert_to_base(amount, from_currency_code):
        currency = HoldingCurrency.objects.filter(code=from_currency_code).first()
        if not currency or currency.is_base_currency:
            return amount

        # amount_base = amount_foreign / exchange_rate
        return amount / currency.exchange_rate_to_base

    @staticmethod
    def convert_from_base(amount_base, to_currency_code):
        currency = HoldingCurrency.objects.filter(code=to_currency_code).first()
        if not currency or currency.is_base_currency:
            return amount_base

        return amount_base * currency.exchange_rate_to_base

    @staticmethod
    def evaluate_fx_risk(exposure_amount, currency_code, volatility_index=0.05):
        """
        Calcula el Valor en Riesgo (VaR) simplificado por fluctuación FX.
        """
        base_val = CurrencyEngine.convert_to_base(exposure_amount, currency_code)
        risk_amount = base_val * Decimal(str(volatility_index))

        return {
            "exposure_base": base_val,
            "potential_impact": risk_amount,
            "risk_level": "HIGH" if volatility_index > 0.1 else "LOW"
        }
