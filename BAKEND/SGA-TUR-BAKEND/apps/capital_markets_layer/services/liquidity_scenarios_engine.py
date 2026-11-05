from decimal import Decimal
from .capital_structure_engine import CapitalStructureEngine
from apps.institutional_layer.services.valuation_engine import ValuationEngine

class LiquidityScenariosEngine:
    """
    Simulador de escenarios de liquidez (M&A, IPO, Dividend Recap) (Fase 8).
    """

    @staticmethod
    def simulate_strategic_sale(multiplier=10.0):
        """
        Simula una venta total del holding a un múltiplo específico.
        """
        valuation = ValuationEngine.calculate_valuation()
        exit_value = valuation['valuation_base'] * (Decimal(str(multiplier)) / Decimal(str(valuation['multiplier_applied'])))

        waterfall = CapitalStructureEngine.calculate_liquidation_waterfall(exit_value)

        return {
            "exit_scenario": "Strategic Sale",
            "implied_valuation": exit_value,
            "multiplier": multiplier,
            "shareholder_returns": waterfall['breakdown']
        }

    @staticmethod
    def simulate_ipo(free_float_percentage=20.0, listing_discount=0.15):
        """
        Simula un IPO con dilución por emisión primaria y descuento de salida.
        """
        valuation = ValuationEngine.calculate_valuation()
        market_cap = valuation['valuation_base'] * (Decimal('1') - Decimal(str(listing_discount)))

        return {
            "exit_scenario": "IPO",
            "market_cap": market_cap,
            "free_float": free_float_percentage,
            "estimated_share_price": market_cap / 1000000, # Simplificado
            "compliance_ready": True # Vinculado a IPOComplianceEngine
        }
