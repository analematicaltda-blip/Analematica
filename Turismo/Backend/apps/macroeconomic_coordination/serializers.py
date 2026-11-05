from rest_framework import serializers
from .models import MacroCouncil, SystemicRiskIndicator, CapitalCoordinationNode, EconomicModelSnapshot, StabilizationProtocol

class MacroCouncilSerializer(serializers.ModelSerializer):
    class Meta:
        model = MacroCouncil
        fields = '__all__'

class SystemicRiskIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemicRiskIndicator
        fields = '__all__'

class CapitalCoordinationNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapitalCoordinationNode
        fields = '__all__'

class EconomicModelSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicModelSnapshot
        fields = '__all__'

class StabilizationProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = StabilizationProtocol
        fields = '__all__'

class MacroDashboardSerializer(serializers.Serializer):
    aggregated_systemic_risk = serializers.DecimalField(max_digits=5, decimal_places=4)
    macro_stability_index = serializers.DecimalField(max_digits=5, decimal_places=4)
    private_buffer_total = serializers.DecimalField(max_digits=25, decimal_places=4)
    active_stabilization_protocols = serializers.IntegerField()
    coordination_level = serializers.IntegerField()
