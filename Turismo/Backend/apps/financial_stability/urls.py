from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StabilityCouncilViewSet, RiskAnalyticsNodeViewSet,
    LiquidityBufferViewSet, ShockAbsorptionViewSet,
    CrisisCaseViewSet, StabilityDashboardViewSet
)

router = DefaultRouter()
router.register(r'councils', StabilityCouncilViewSet, basename='stability_councils')
router.register(r'risk-nodes', RiskAnalyticsNodeViewSet, basename='stability_nodes')
router.register(r'buffers', LiquidityBufferViewSet, basename='stability_buffers')
router.register(r'shock-absorption', ShockAbsorptionViewSet, basename='stability_policies')
router.register(r'crisis-cases', CrisisCaseViewSet, basename='stability_crisis')
router.register(r'dashboard', StabilityDashboardViewSet, basename='stability_dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
