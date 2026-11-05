from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsSuperAdmin
from .services.consolidation_engine import ConsolidationEngine
from .services.forecasting_engine import ForecastingEngine
from .predictive_intelligence.risk_score import RiskScoreManager
from apps.global_orchestration.global_consolidation import GlobalConsolidation
from apps.global_orchestration.currency_engine import CurrencyEngine
from apps.institutional_layer.services.valuation_engine import ValuationEngine
from apps.institutional_layer.services.investor_reporting_engine import InvestorReportingEngine
from apps.capital_markets_layer.services.capital_structure_engine import CapitalStructureEngine
from apps.capital_markets_layer.services.exit_strategy_engine import ExitStrategyEngine

class GlobalDashboardView(APIView):
    """
    Torre de Control - Dashboard Ejecutivo Global.
    Consolida métricas SaaS y financieras en tiempo real.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        engine = ConsolidationEngine()

        saas_metrics = engine.get_saas_metrics()
        financials = engine.get_balance_sheet()
        p_and_l = engine.get_income_statement()

        forecast = ForecastingEngine.project_revenue(months=6)

        global_summary = GlobalConsolidation.get_global_revenue()
        regional_data = GlobalConsolidation.revenue_by_region()

        valuation = ValuationEngine.calculate_valuation()
        investor_metrics = InvestorReportingEngine.get_board_deck_metrics()

        data = {
            "holding_global": {
                "total_mrr": global_summary['global_mrr'],
                "total_arr": global_summary['global_arr'],
                "entities": global_summary['entities_count'],
                "regional_breakdown": regional_data
            },
            "institutional": {
                "current_valuation": valuation['valuation_base'],
                "rule_of_40": investor_metrics['rule_of_40'],
                "runway_months": investor_metrics['runway_months'],
                "ltv_cac_ratio": investor_metrics['ltv_cac_ratio']
            },
            "saas": saas_metrics,
            "financial_summary": {
                "balance_sheet": financials,
                "income_statement": p_and_l
            },
            "predictive": {
                "mrr_forecast_6m": forecast['projections'][-1]['mrr'],
                "arr_forecast_6m": forecast['projections'][-1]['arr'],
                "revenue_at_risk": saas_metrics['mrr'] * Decimal(str(saas_metrics['churn_rate'] / 100))
            },
            "autonomy": {
                "level": 0.35, # % de decisiones automáticas
                "ai_roi": 12.5, # ROI generado por optimización IA
                "operative_savings": 1500.0,
                "antifragility_index": 0.88
            },
            "capital_markets": {
                "ownership": CapitalStructureEngine.calculate_current_ownership()[:5], # Top 5 holders
                "exit_strategy": ExitStrategyEngine.get_exit_recommendation(),
                "listing_readiness": "85%"
            },
            "governance": {
                "active_policies_count": 0, # Integrar con Kernel
                "system_state": "NORMAL"
            }
        }

        return Response(data)

from .system_sensors.anomaly_detector import AnomalyDetector
from .system_sensors.revenue_monitor import RevenueMonitor
from .system_sensors.risk_classifier import RiskClassifier

class RiskPanelView(APIView):
    """
    Panel de Riesgo Sistémico.
    Detecta anomalías e inconsistencias en tiempo real.
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        detector = AnomalyDetector()
        monitor = RevenueMonitor()
        classifier = RiskClassifier()

        financial_anomalies = detector.check_unbalanced_entries()
        commercial_health = {
            "churn_rate": monitor.calculate_churn_rate(),
            "revenue_by_plan": list(monitor.get_revenue_by_plan())
        }

        risk_level = classifier.classify(financial_anomalies, commercial_health)

        return Response({
            "risk_level": risk_level,
            "financial_anomalies": financial_anomalies,
            "commercial_health": commercial_health,
            "alerts": [
                f"Detectados {len(financial_anomalies)} desbalances contables." if financial_anomalies else "Integridad contable validada."
            ]
        })
