from rest_framework import serializers
from .models import SaaSMetric, CohortAnalysis, ChurnRiskScore, RevenueForecast, UnitEconomics, OperationalRiskIndex

class SaaSMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaaSMetric
        fields = '__all__'

class CohortAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = CohortAnalysis
        fields = '__all__'

class ChurnRiskScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChurnRiskScore
        fields = '__all__'

class RevenueForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = RevenueForecast
        fields = '__all__'

class UnitEconomicsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitEconomics
        fields = '__all__'

class OperationalRiskIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationalRiskIndex
        fields = '__all__'
