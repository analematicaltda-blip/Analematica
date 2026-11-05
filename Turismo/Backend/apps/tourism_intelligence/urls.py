from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import IntelligenceViewSet, TouristBehaviorViewSet, SeasonalityViewSet

router = DefaultRouter()
router.register(r'intelligence', IntelligenceViewSet, basename='tourism-intelligence')
router.register(r'behavior', TouristBehaviorViewSet, basename='tourist-behavior')
router.register(r'seasonality', SeasonalityViewSet, basename='tourism-seasonality')

urlpatterns = [
    path('', include(router.urls)),
]
