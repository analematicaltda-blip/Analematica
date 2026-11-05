from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MetaEcosystemViewSet, EcosystemInterdependenceViewSet,
    InteroperabilityProtocolViewSet, GlobalUtilityMetricViewSet,
    MetaLiquidityPoolViewSet, MetaDashboardViewSet
)

router = DefaultRouter()
router.register(r'ecosystems', MetaEcosystemViewSet, basename='meta_eco')
router.register(r'interdependences', EcosystemInterdependenceViewSet, basename='meta_deps')
router.register(r'protocols', InteroperabilityProtocolViewSet, basename='meta_protocols')
router.register(r'utility-metrics', GlobalUtilityMetricViewSet, basename='meta_utility')
router.register(r'liquidity-pools', MetaLiquidityPoolViewSet, basename='meta_pools')
router.register(r'dashboard', MetaDashboardViewSet, basename='meta_dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
