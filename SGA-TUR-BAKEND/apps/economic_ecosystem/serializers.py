from rest_framework import serializers
from .models import EconomicNode, EconomicFlow, InternalContract, EcosystemIncentive

class EconomicNodeSerializer(serializers.ModelSerializer):
    contribution_value = serializers.SerializerMethodField()

    class Meta:
        model = EconomicNode
        fields = '__all__'

    def get_contribution_value(self, obj):
        from .application.orchestration_service import OrchestrationService
        return OrchestrationService.calculate_node_value(obj)

class EconomicFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = EconomicFlow
        fields = '__all__'

class InternalContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalContract
        fields = '__all__'

class EcosystemIncentiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcosystemIncentive
        fields = '__all__'

class EcosystemMetricsSerializer(serializers.Serializer):
    ecosystem_value = serializers.DecimalField(max_digits=20, decimal_places=4)
    global_risk = serializers.DecimalField(max_digits=10, decimal_places=4)
    node_count = serializers.IntegerField()
    isolated_nodes = serializers.IntegerField()
