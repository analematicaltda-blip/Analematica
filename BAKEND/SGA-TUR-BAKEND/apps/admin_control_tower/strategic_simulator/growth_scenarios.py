from decimal import Decimal

class GrowthSimulator:
    """
    Simula escenarios de crecimiento por adquisición de nuevos tenants.
    """

    @staticmethod
    def simulate_acquisition(new_tenants, avg_mrr):
        impact = Decimal(str(new_tenants)) * Decimal(str(avg_mrr))

        return {
            "new_tenants": new_tenants,
            "mrr_expansion": impact,
            "arr_expansion": impact * 12
        }
