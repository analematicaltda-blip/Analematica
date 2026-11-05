from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SaaSLeadViewSet, SaaSSubscriptionViewSet,
    CommercialKPIViewSet, SaaSPlanViewSet
)

router = DefaultRouter()
router.register(r'leads', SaaSLeadViewSet, basename='saas-lead')
router.register(r'subscriptions', SaaSSubscriptionViewSet, basename='saas-subscription')
router.register(r'kpis', CommercialKPIViewSet, basename='saas-kpi')
router.register(r'plans', SaaSPlanViewSet, basename='saas-plan')

urlpatterns = [
    path('', include(router.urls)),
]
