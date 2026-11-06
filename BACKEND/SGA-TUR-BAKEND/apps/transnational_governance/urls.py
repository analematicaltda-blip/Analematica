from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    GovernanceBodyViewSet, GovernanceMemberViewSet,
    AlgorithmicAuditViewSet, DisputeCaseViewSet,
    GovernanceDashboardViewSet
)

router = DefaultRouter()
router.register(r'bodies', GovernanceBodyViewSet, basename='gov_bodies')
router.register(r'members', GovernanceMemberViewSet, basename='gov_members')
router.register(r'audits', AlgorithmicAuditViewSet, basename='gov_audits')
router.register(r'disputes', DisputeCaseViewSet, basename='gov_disputes')
router.register(r'dashboard', GovernanceDashboardViewSet, basename='gov_dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
