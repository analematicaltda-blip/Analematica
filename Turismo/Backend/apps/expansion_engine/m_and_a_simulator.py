from decimal import Decimal

class MASimulator:
    """
    Simulates corporate acquisitions and calculates synergies.
    """

    @staticmethod
    def simulate_acquisition(target_mrr, target_costs, purchase_price):
        # 1. New Combined MRR
        # 2. Synergy Calculation (Cost reduction of 20% by integrating infrastructure)
        synergies = target_costs * Decimal('0.20')
        combined_ebitda = (target_mrr * 12) - (target_costs - synergies)

        # 3. Payback Period
        if combined_ebitda > 0:
            payback_years = purchase_price / combined_ebitda
        else:
            payback_years = 99

        return {
            'combined_annual_revenue': target_mrr * 12,
            'estimated_synergies': synergies,
            'combined_ebitda': combined_ebitda,
            'payback_period_years': round(payback_years, 2)
        }
