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

    def get_queryset(self):
        # Private management of the requesting customer's own reviews.
        return super().get_queryset().filter(customer=self.request.user)

    def perform_create(self, serializer):
        from django.db import IntegrityError,transaction
        from rest_framework.exceptions import ValidationError
        try:
            with transaction.atomic():serializer.save(customer=self.request.user,is_verified_purchase=False)
        except IntegrityError:
            raise ValidationError('No se pudo crear la reseña; comprueba si ya existe para este servicio.') from None

class ProviderReputationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProviderReputation.objects.all()
    serializer_class = ProviderReputationSerializer
