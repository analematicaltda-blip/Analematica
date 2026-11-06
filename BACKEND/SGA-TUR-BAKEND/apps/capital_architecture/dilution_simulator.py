from decimal import Decimal
from .cap_table_engine import CapTableEngine
from .valuation_engine import ValuationEngine

class DilutionSimulator:
    """
    Simulates the impact of funding rounds on ownership and control.
    """

    @staticmethod
    def simulate_series_a(new_capital):
        valuation = ValuationEngine.calculate_valuation()
        pre_money_valuation = valuation['valuation']
        post_money_valuation = pre_money_valuation + new_capital

        investor_ownership = (new_capital / post_money_valuation) * 100
        founder_dilution = 1 - (pre_money_valuation / post_money_valuation)

        return {
            'pre_money_valuation': pre_money_valuation,
            'post_money_valuation': post_money_valuation,
            'investor_ownership_percentage': round(investor_ownership, 2),
            'founder_dilution_percentage': round(founder_dilution * 100, 2)
        }
