from rest_framework import serializers
from .models import (
    OptimizationProposal,
    PerformanceMetric,
    AutonomousAction,
    AutonomousExecutionLog,
    AutonomyControl
)

class OptimizationProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizationProposal
        fields = '__all__'

class AutonomousActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutonomousAction
        fields = '__all__'

class AutonomousExecutionLogSerializer(serializers.ModelSerializer):
    action_name = serializers.ReadOnlyField(source='action.name')
    class Meta:
        model = AutonomousExecutionLog
        fields = '__all__'

class AutonomyControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutonomyControl
        fields = '__all__'
