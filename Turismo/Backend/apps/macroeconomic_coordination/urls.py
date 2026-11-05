from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MacroCouncilViewSet, SystemicRiskViewSet,
    CapitalCoordinationViewSet, EconomicModelViewSet,
    StabilizationProtocolViewSet, MacroDashboardViewSet
)

router = DefaultRouter()
router.register(r'councils', MacroCouncilViewSet, basename='macro_councils')
router.register(r'risk-indicators', SystemicRiskViewSet, basename='macro_risk')
router.register(r'coordination-nodes', CapitalCoordinationViewSet, basename='macro_nodes')
router.register(r'model-snapshots', EconomicModelViewSet, basename='macro_models')
router.register(r'stabilization-protocols', StabilizationProtocolViewSet, basename='macro_protocols')
router.register(r'dashboard', MacroDashboardViewSet, basename='macro_dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
