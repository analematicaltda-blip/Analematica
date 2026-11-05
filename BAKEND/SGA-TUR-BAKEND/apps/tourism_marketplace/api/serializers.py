from rest_framework import serializers
from ..models import ProviderReputation, TourismReview, ProductRanking, TourismPromotion, TourismConversionMetrics
from apps.turismo.serializers.provider_serializers import TourismServiceSerializer

class ProviderReputationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderReputation
        fields = '__all__'

class TourismReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)

    class Meta:
        model = TourismReview
        fields = ['id', 'customer', 'customer_name', 'service', 'rating', 'comment', 'is_verified_purchase', 'created_at']

class ProductRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRanking
        fields = '__all__'

class TourismPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismPromotion
        fields = '__all__'

class TourismConversionMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismConversionMetrics
        fields = '__all__'
