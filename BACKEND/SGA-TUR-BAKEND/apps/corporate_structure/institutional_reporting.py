from .consolidation_engine import ConsolidationEngine
from apps.capital_architecture.cap_table_engine import CapTableEngine
from apps.capital_architecture.valuation_engine import ValuationEngine
from apps.operational_intelligence.metrics_engine import MetricsEngine
from apps.operational_intelligence.forecast_engine import ForecastEngine

class InstitutionalReporting:
    """
    Generates high-level reports for the Board and Investors.
    """

    @staticmethod
    def generate_investor_report(holding_id):
        consolidation = ConsolidationEngine.consolidate_holding(holding_id)
        cap_table = CapTableEngine.get_full_cap_table()
        valuation = ValuationEngine.calculate_valuation()
        saas_metrics = MetricsEngine.calculate_all()

        return {
            'holding_performance': consolidation,
            'saas_kpis': saas_metrics,
            'valuation': valuation,
            'equity_summary': {
                'total_shares': cap_table['total_shares'],
                'top_shareholders': cap_table['data'][:5]
            },
            'burn_runway': {
                'months_remaining': 18 # Placeholder for calculation
            }
        }
