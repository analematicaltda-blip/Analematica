from rest_framework import serializers
from .domain.policy import EnterprisePolicy
from .domain.strategic_objective import StrategicObjective
from .domain.budget import CorporateBudget
from .domain.workflow import EnterpriseWorkflow, WorkflowStep
from .domain.logs import DecisionLog, PolicyEvaluationLog
from .domain.autonomous import LearningLoopRecord, AutonomousActionRecord, CashOptimizationProposal, SelfHealingAudit
from .domain.intelligence import ScenarioSimulation, RollingForecast
from .domain.decision_engine import RiskExposure, EnterpriseDecisionRule

class EnterprisePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterprisePolicy
        fields = '__all__'

class StrategicObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StrategicObjective
        fields = '__all__'

class CorporateBudgetSerializer(serializers.ModelSerializer):
    variance_revenue = serializers.SerializerMethodField()

    class Meta:
        model = CorporateBudget
        fields = '__all__'

    def get_variance_revenue(self, obj):
        return obj.actual_revenue - obj.revenue_target

class EnterpriseWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseWorkflow
        fields = '__all__'

class DecisionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecisionLog
        fields = '__all__'

class ScenarioSimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioSimulation
        fields = '__all__'

class RollingForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = RollingForecast
        fields = '__all__'

class RiskExposureSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskExposure
        fields = '__all__'

class DecisionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnterpriseDecisionRule
        fields = '__all__'

class LearningLoopSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningLoopRecord
        fields = '__all__'

class AutonomousActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutonomousActionRecord
        fields = '__all__'

class CashProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashOptimizationProposal
        fields = '__all__'

class SelfHealingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfHealingAudit
        fields = '__all__'
