from rest_framework import serializers
from .models import StateEntity, IntegrationProtocol, SovereignComplianceNode, InfrastructureProject, JointGovernanceCommittee

class StateEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = StateEntity
        fields = '__all__'

class IntegrationProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationProtocol
        fields = '__all__'

class SovereignComplianceNodeSerializer(serializers.ModelSerializer):
    integrated_utility = serializers.SerializerMethodField()

    class Meta:
        model = SovereignComplianceNode
        fields = '__all__'

    def get_integrated_utility(self, obj):
        from .application.compliance_service import SovereignComplianceService
        return SovereignComplianceService.calculate_integrated_utility(obj.id)

class InfrastructureProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = InfrastructureProject
        fields = '__all__'

class JointGovernanceCommitteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JointGovernanceCommittee
        fields = '__all__'

class StateDashboardSerializer(serializers.Serializer):
    compliance_score = serializers.DecimalField(max_digits=5, decimal_places=4)
    integrated_utility = serializers.DecimalField(max_digits=15, decimal_places=4)
    infrastructure_commitment = serializers.DecimalField(max_digits=20, decimal_places=4)
    certified_entities = serializers.IntegerField()
    active_projects = serializers.IntegerField()
