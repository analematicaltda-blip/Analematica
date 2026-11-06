from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TokenizedAssetViewSet,
    ProgrammableUnitViewSet,
    GovernanceRuleViewSet,
    DigitalRegistryViewSet,
    ComplianceConstraintViewSet
)

router = DefaultRouter()
router.register(r'assets', TokenizedAssetViewSet, basename='tokenized-asset')
router.register(r'units', ProgrammableUnitViewSet, basename='tokenized-unit')
router.register(r'rules', GovernanceRuleViewSet, basename='tokenized-rule')
router.register(r'registry', DigitalRegistryViewSet, basename='tokenized-registry')
router.register(r'compliance', ComplianceConstraintViewSet, basename='tokenized-compliance')

urlpatterns = [
    path('', include(router.urls)),
]
