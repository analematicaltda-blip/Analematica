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
        read_only_fields = ['id','customer','customer_name','is_verified_purchase','created_at']

    def validate(self,attrs):
        if not self.instance and attrs.get('service') and TourismReview.objects.filter(customer=self.context['request'].user,service=attrs['service']).exists():
            raise serializers.ValidationError('Ya existe una reseña tuya para este servicio.')
        if self.instance and 'service' in attrs and attrs['service'].pk!=self.instance.service_id:
            raise serializers.ValidationError({'service':'No se puede trasladar una reseña a otro servicio.'})
        return attrs

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
