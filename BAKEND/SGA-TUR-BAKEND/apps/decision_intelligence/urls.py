from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StrategyProposalViewSet, DecisionMatrixViewSet

router = DefaultRouter()
router.register(r'proposals', StrategyProposalViewSet)
router.register(r'matrix', DecisionMatrixViewSet)

app_name = 'decision_intelligence'

urlpatterns = [
    path('', include(router.urls)),
]
