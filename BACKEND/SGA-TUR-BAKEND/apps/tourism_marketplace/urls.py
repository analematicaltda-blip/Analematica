from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.views import MarketplaceViewSet, TourismReviewViewSet, ProviderReputationViewSet

router = DefaultRouter()
router.register(r'discovery', MarketplaceViewSet, basename='marketplace-discovery')
router.register(r'reviews', TourismReviewViewSet, basename='tourism-review')
router.register(r'reputation', ProviderReputationViewSet, basename='provider-reputation')

urlpatterns = [
    path('', include(router.urls)),
]
