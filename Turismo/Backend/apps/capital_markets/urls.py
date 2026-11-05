from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CapitalStructureViewSet,
    DebtInstrumentViewSet,
    EquityInstrumentViewSet,
    MarketRatingViewSet,
    StructuredDealViewSet
)

router = DefaultRouter()
router.register(r'structure', CapitalStructureViewSet, basename='capital-structure')
router.register(r'debt', DebtInstrumentViewSet, basename='market-debt')
router.register(r'equity', EquityInstrumentViewSet, basename='market-equity')
router.register(r'ratings', MarketRatingViewSet, basename='market-rating')
router.register(r'structured-deals', StructuredDealViewSet, basename='market-structured')

urlpatterns = [
    path('', include(router.urls)),
]
