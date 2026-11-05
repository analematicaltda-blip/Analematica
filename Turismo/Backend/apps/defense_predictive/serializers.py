from rest_framework import serializers
from .models import ThreatNode, ThreatEdge, PredictiveScenario, PreventiveHardening

class ThreatNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatNode
        fields = '__all__'

class PredictiveScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictiveScenario
        fields = '__all__'

class PreventiveHardeningSerializer(serializers.ModelSerializer):
    target_node_name = serializers.CharField(source='target_node.name', read_only=True)
    class Meta:
        model = PreventiveHardening
        fields = '__all__'
