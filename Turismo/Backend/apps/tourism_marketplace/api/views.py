from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import ProviderReputation, TourismReview, ProductRanking, TourismPromotion, TourismConversionMetrics
from .serializers import (
    ProviderReputationSerializer, TourismReviewSerializer,
    ProductRankingSerializer, TourismPromotionSerializer, TourismConversionMetricsSerializer
)
from ..services import TourismRecommendationService

class MarketplaceViewSet(viewsets.ViewSet):
    """
    Controlador para operaciones inteligentes del Marketplace.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        recommendations = TourismRecommendationService.get_personalized_recommendations(request.user)
        from apps.turismo.serializers.provider_serializers import TourismServiceSerializer
        serializer = TourismServiceSerializer(recommendations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trending(self, request):
        trending = TourismRecommendationService.get_trending_services()
        from apps.turismo.serializers.provider_serializers import TourismServiceSerializer
        serializer = TourismServiceSerializer(trending, many=True)
        return Response(serializer.data)

class TourismReviewViewSet(viewsets.ModelViewSet):
    queryset = TourismReview.objects.all()
    serializer_class = TourismReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class ProviderReputationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProviderReputation.objects.all()
    serializer_class = ProviderReputationSerializer
