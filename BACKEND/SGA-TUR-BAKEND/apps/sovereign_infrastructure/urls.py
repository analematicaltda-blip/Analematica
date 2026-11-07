from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JurisdictionalNodeViewSet, RegulatoryProfileViewSet,
    CapitalShieldViewSet, DigitalInfraBackupViewSet,
    CorporateConstitutionViewSet, SovereignDashboardViewSet
)

router = DefaultRouter()
router.register(r'jurisdictional-nodes', JurisdictionalNodeViewSet, basename='sov_nodes')
router.register(r'regulatory-profiles', RegulatoryProfileViewSet, basename='sov_profiles')
router.register(r'capital-shields', CapitalShieldViewSet, basename='sov_shields')
router.register(r'infra-backups', DigitalInfraBackupViewSet, basename='sov_backups')
router.register(r'constitution', CorporateConstitutionViewSet, basename='sov_constitution')
router.register(r'dashboard', SovereignDashboardViewSet, basename='sov_dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
