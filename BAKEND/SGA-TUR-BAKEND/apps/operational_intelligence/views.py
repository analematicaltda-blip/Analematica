from rest_framework import viewsets, views
from rest_framework.response import Response
from .models import SaaSMetric, CohortAnalysis, ChurnRiskScore, RevenueForecast, UnitEconomics, OperationalRiskIndex
from .serializers import *
from .metrics_engine import MetricsEngine
from .cohort_engine import CohortEngine
from .churn_engine import ChurnEngine
from .forecast_engine import ForecastEngine
from .unit_economics_engine import UnitEconomicsEngine
from .risk_scoring_engine import RiskScoringEngine
from .pricing_optimizer import PricingOptimizer

class IntelligenceDashboardView(views.APIView):
    """
    Consolidated view for the Operational Intelligence Dashboard.
    """
    def get(self, request):
        # Trigger engines to update data (In production this would be a background task)
        # For certification, we run it on demand
        MetricsEngine.calculate_all()
        CohortEngine.run_analysis()
        ChurnEngine.evaluate_all_customers()
        ForecastEngine.generate_forecasts()
        UnitEconomicsEngine.calculate_all()
        RiskScoringEngine.calculate_global_risk()

        data = {
            'core_metrics': MetricsEngine.calculate_all(),
            'cohorts': CohortAnalysisSerializer(CohortAnalysis.objects.all()[:20], many=True).data,
            'high_risk_customers': ChurnRiskScoreSerializer(ChurnRiskScore.objects.filter(risk_level='HIGH'), many=True).data,
            'forecasts': RevenueForecastSerializer(RevenueForecast.objects.all().order_by('forecast_date'), many=True).data,
            'global_risk': OperationalRiskIndexSerializer(OperationalRiskIndex.objects.last()).data,
            'pricing_recommendations': PricingOptimizer.get_recommendations()
        }
        return Response(data)

class ChurnRiskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ChurnRiskScore.objects.all()
    serializer_class = ChurnRiskScoreSerializer

class ForecastViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RevenueForecast.objects.all()
    serializer_class = RevenueForecastSerializer

class UnitEconomicsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UnitEconomics.objects.all()
    serializer_class = UnitEconomicsSerializer
