from rest_framework import serializers
from ..models import (
    TourismDemandForecast, TourismSeasonality, TouristBehaviorProfile,
    TourismFlowAnalytics, TourismEconomicImpact, ConversationalIntent, ConversationalKPI
)

class TourismDemandForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismDemandForecast
        fields = '__all__'

class TourismSeasonalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismSeasonality
        fields = '__all__'

class TouristBehaviorProfileSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='usuario.get_full_name', read_only=True)
    class Meta:
        model = TouristBehaviorProfile
        fields = '__all__'

class TourismFlowAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismFlowAnalytics
        fields = '__all__'

class TourismEconomicImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismEconomicImpact
        fields = '__all__'

class ConversationalIntentSerializer(serializers.ModelSerializer):
    tourist_name = serializers.CharField(source='tourist.get_full_name', read_only=True)
    class Meta:
        model = ConversationalIntent
        fields = '__all__'

class ConversationalKPISerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    class Meta:
        model = ConversationalKPI
        fields = '__all__'
