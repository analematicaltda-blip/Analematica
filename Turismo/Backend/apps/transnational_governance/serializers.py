from rest_framework import serializers
from .models import GovernanceBody, GovernanceMember, AlgorithmicAudit, DisputeCase, GovernanceStabilityMetric

class GovernanceBodySerializer(serializers.ModelSerializer):
    stability_index = serializers.SerializerMethodField()

    class Meta:
        model = GovernanceBody
        fields = '__all__'

    def get_stability_index(self, obj):
        from .application.oversight_service import AlgorithmicOversightService
        return AlgorithmicOversightService.calculate_governance_stability(obj.id)

class GovernanceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernanceMember
        fields = '__all__'

class AlgorithmicAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlgorithmicAudit
        fields = '__all__'

class DisputeCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisputeCase
        fields = '__all__'

class GovernanceStabilityMetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = GovernanceStabilityMetric
        fields = '__all__'

class GovernanceDashboardSerializer(serializers.Serializer):
    institutional_stability = serializers.DecimalField(max_digits=5, decimal_places=4)
    active_disputes = serializers.IntegerField()
    certified_algorithms = serializers.IntegerField()
    governance_level_active = serializers.IntegerField()
    audit_coverage = serializers.DecimalField(max_digits=5, decimal_places=4)
