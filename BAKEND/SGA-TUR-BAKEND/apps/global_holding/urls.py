from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JurisdictionViewSet,
    CapitalAllocationViewSet,
    TaxStrategyViewSet,
    GlobalTreasuryViewSet,
    MacroScenarioViewSet
)

router = DefaultRouter()
router.register(r'jurisdictions', JurisdictionViewSet, basename='global-holding-jurisdiction')
router.register(r'allocations', CapitalAllocationViewSet, basename='global-holding-allocation')
router.register(r'tax-strategies', TaxStrategyViewSet, basename='global-holding-tax')
router.register(r'treasury', GlobalTreasuryViewSet, basename='global-holding-treasury')
router.register(r'scenarios', MacroScenarioViewSet, basename='global-holding-scenario')

urlpatterns = [
    path('', include(router.urls)),
]
