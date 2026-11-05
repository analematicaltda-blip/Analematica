from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StateEntityViewSet, IntegrationProtocolViewSet,
    SovereignComplianceNodeViewSet, InfrastructureProjectViewSet,
    JointGovernanceCommitteeViewSet, StateDashboardViewSet
)

router = DefaultRouter()
router.register(r'entities', StateEntityViewSet, basename='state_entities')
router.register(r'protocols', IntegrationProtocolViewSet, basename='state_protocols')
router.register(r'compliance-nodes', SovereignComplianceNodeViewSet, basename='state_compliance')
router.register(r'projects', InfrastructureProjectViewSet, basename='state_projects')
router.register(r'committees', JointGovernanceCommitteeViewSet, basename='state_committees')
router.register(r'dashboard', StateDashboardViewSet, basename='state_dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
