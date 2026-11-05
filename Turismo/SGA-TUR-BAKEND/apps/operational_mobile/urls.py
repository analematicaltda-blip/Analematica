from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OperatorViewSet, OperatorTrackingViewSet, OperationReportViewSet

router = DefaultRouter()
router.register(r'operators', OperatorViewSet, basename='operator')
router.register(r'tracking', OperatorTrackingViewSet, basename='operator-tracking')
router.register(r'reports', OperationReportViewSet, basename='operation-report')

urlpatterns = [
    path('', include(router.urls)),
]
