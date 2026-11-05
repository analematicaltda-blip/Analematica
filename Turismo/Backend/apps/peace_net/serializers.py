from rest_framework import serializers
from .models import SystemicRiskIndicator, StabilityAlert, MitigationScenario

class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemicRiskIndicator
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = StabilityAlert
        fields = '__all__'

class ScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = MitigationScenario
        fields = '__all__'
