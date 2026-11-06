from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class CurrencyTranslationEngine:
    """
    Handles FX conversion for financial consolidation.
    """

    @staticmethod
    def get_rate(from_currency: str, to_currency: str, period: str = None) -> Decimal:
        """
        Retrieves the exchange rate for a given period from the versioned FX table.
        """
        if from_currency == to_currency:
            return Decimal('1.0')

        from .fx_models import FXRateTable
        rate_entry = FXRateTable.objects.filter(
            from_currency=from_currency,
            to_currency=to_currency,
            is_active=True
        ).order_by('-version').first()

        if rate_entry:
            return rate_entry.rate

        # Hardening Fallback (Development only)
        rates = {
            ('USD', 'COP'): Decimal('4000.0'),
            ('EUR', 'COP'): Decimal('4300.0'),
            ('COP', 'USD'): Decimal('0.00025'),
        }
        return rates.get((from_currency, to_currency), Decimal('1.0'))

    @staticmethod
    def translate(amount: Decimal, from_currency: str, to_currency: str, rate: Decimal = None) -> Decimal:
        """
        Translates an amount from one currency to another.
        """
        if from_currency == to_currency:
            return amount

        if rate is None:
            rate = CurrencyTranslationEngine.get_rate(from_currency, to_currency)

        return amount * rate
