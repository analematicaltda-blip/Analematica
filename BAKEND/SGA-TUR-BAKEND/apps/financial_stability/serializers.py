from rest_framework import serializers
from .models import StabilityCouncil, RiskAnalyticsNode, LiquidityBuffer, ShockAbsorptionPolicy, CrisisCase

class StabilityCouncilSerializer(serializers.ModelSerializer):
    class Meta:
        model = StabilityCouncil
        fields = '__all__'

class RiskAnalyticsNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAnalyticsNode
        fields = '__all__'

class LiquidityBufferSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiquidityBuffer
        fields = '__all__'

class ShockAbsorptionPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShockAbsorptionPolicy
        fields = '__all__'

class CrisisCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrisisCase
        fields = '__all__'

class StabilityDashboardSerializer(serializers.Serializer):
    global_risk_index = serializers.DecimalField(max_digits=10, decimal_places=4)
    monitoring_status = serializers.CharField()
    total_stabilization_liquidity = serializers.DecimalField(max_digits=25, decimal_places=4)
    active_crisis_cases = serializers.IntegerField()
    buffer_adequacy_ratio = serializers.DecimalField(max_digits=5, decimal_places=4)
