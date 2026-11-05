from decimal import Decimal

class MNASimulationEngine:
    """
    Motor de simulación de adquisiciones y fusiones (M&A) (Fase 8).
    """

    @staticmethod
    def simulate_acquisition(target_arr, target_ebitda, synergetic_cost_savings):
        """
        Simula la adquisición de un competidor.
        """
        revenue_synergy = Decimal(str(target_arr)) * Decimal('0.15') # 15% cross-sell

        impact_ebitda = Decimal(str(target_ebitda)) + Decimal(str(synergetic_cost_savings)) + revenue_synergy

        return {
            "pro_forma_arr_addition": target_arr + float(revenue_synergy),
            "ebitda_impact": impact_ebitda,
            "valuation_accretion": impact_ebitda * Decimal('15'), # Múltiplo estratégico
            "synergies_identified": [
                "Infrastructure consolidation",
                "Cross-sell to regional base",
                "Sales team optimization"
            ]
        }
