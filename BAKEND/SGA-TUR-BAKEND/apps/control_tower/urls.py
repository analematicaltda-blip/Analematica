from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import KPIViewSet, AlertViewSet, ThresholdViewSet, ExecutiveDashboardView

router = DefaultRouter()
router.register(r'kpis', KPIViewSet, basename='control-tower-kpi')
router.register(r'alerts', AlertViewSet, basename='control-tower-alert')
router.register(r'thresholds', ThresholdViewSet, basename='control-tower-threshold')

urlpatterns = [
    path('dashboard/', ExecutiveDashboardView.as_view(), name='executive-dashboard'),
    path('', include(router.urls)),
]
