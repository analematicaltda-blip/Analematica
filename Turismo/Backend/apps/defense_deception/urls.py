from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GhostSurfaceViewSet, AdversarialProfileViewSet, DisuasionStatsView

router = DefaultRouter()
router.register(r'ghost-surfaces', GhostSurfaceViewSet)
router.register(r'adversaries', AdversarialProfileViewSet)

app_name = 'defense_deception'

urlpatterns = [
    path('stats/', DisuasionStatsView.as_view(), name='disuasion-stats'),
    path('', include(router.urls)),
]
