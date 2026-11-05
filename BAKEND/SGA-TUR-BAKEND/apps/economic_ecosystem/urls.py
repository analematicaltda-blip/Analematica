from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EconomicNodeViewSet, EconomicFlowViewSet,
    InternalContractViewSet, EcosystemIncentiveViewSet,
    EcosystemDashboardViewSet
)

router = DefaultRouter()
router.register(r'nodes', EconomicNodeViewSet, basename='eco_nodes')
router.register(r'flows', EconomicFlowViewSet, basename='eco_flows')
router.register(r'contracts', InternalContractViewSet, basename='eco_contracts')
router.register(r'incentives', EcosystemIncentiveViewSet, basename='eco_incentives')
router.register(r'dashboard', EcosystemDashboardViewSet, basename='eco_dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
