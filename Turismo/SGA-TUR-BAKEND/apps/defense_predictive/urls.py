from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThreatNodeViewSet, PredictiveScenarioViewSet, PreventiveHardeningViewSet

router = DefaultRouter()
router.register(r'nodes', ThreatNodeViewSet)
router.register(r'scenarios', PredictiveScenarioViewSet)
router.register(r'hardening-actions', PreventiveHardeningViewSet)

app_name = 'defense_predictive'

urlpatterns = [
    path('', include(router.urls)),
]
