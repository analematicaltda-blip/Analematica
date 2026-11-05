from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OptimizationProposalViewSet,
    AutonomousActionViewSet,
    AutonomousExecutionLogViewSet,
    AutonomyControlViewSet
)

router = DefaultRouter()
router.register(r'proposals', OptimizationProposalViewSet)
router.register(r'actions', AutonomousActionViewSet)
router.register(r'logs', AutonomousExecutionLogViewSet)
router.register(r'controls', AutonomyControlViewSet)

app_name = 'ecosystem_optimization'

urlpatterns = [
    path('', include(router.urls)),
]
