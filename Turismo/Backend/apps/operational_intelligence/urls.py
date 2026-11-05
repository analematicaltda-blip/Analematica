from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntelligenceDashboardView, ChurnRiskViewSet, ForecastViewSet, UnitEconomicsViewSet

router = DefaultRouter()
router.register(r'churn-risk', ChurnRiskViewSet)
router.register(r'forecasts', ForecastViewSet)
router.register(r'unit-economics', UnitEconomicsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', IntelligenceDashboardView.as_view(), name='intelligence-dashboard'),
]
