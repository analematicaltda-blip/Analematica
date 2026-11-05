from rest_framework import viewsets, permissions
from .domain.policy import EnterprisePolicy
from .domain.strategic_objective import StrategicObjective
from .domain.budget import CorporateBudget
from .domain.workflow import EnterpriseWorkflow
from .domain.logs import DecisionLog
from .domain.intelligence import ScenarioSimulation, RollingForecast
from .domain.decision_engine import RiskExposure, EnterpriseDecisionRule
from .domain.autonomous import LearningLoopRecord, AutonomousActionRecord, CashOptimizationProposal, SelfHealingAudit
from .serializers import (
    EnterprisePolicySerializer, StrategicObjectiveSerializer,
    CorporateBudgetSerializer, EnterpriseWorkflowSerializer,
    DecisionLogSerializer, ScenarioSimulationSerializer,
    RollingForecastSerializer, RiskExposureSerializer, DecisionRuleSerializer,
    LearningLoopSerializer, AutonomousActionSerializer, CashProposalSerializer, SelfHealingSerializer
)
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class EnterprisePolicyViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = EnterprisePolicy.objects.all()
    serializer_class = EnterprisePolicySerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class StrategicObjectiveViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = StrategicObjective.objects.all()
    serializer_class = StrategicObjectiveSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class CorporateBudgetViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = CorporateBudget.objects.all()
    serializer_class = CorporateBudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class EnterpriseWorkflowViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = EnterpriseWorkflow.objects.all()
    serializer_class = EnterpriseWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class DecisionLogViewSet(SystemicERPViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = DecisionLog.objects.all()
    serializer_class = DecisionLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ScenarioSimulationViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = ScenarioSimulation.objects.all()
    serializer_class = ScenarioSimulationSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class RollingForecastViewSet(SystemicERPViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RollingForecast.objects.all()
    serializer_class = RollingForecastSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class RiskExposureViewSet(SystemicERPViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = RiskExposure.objects.all()
    serializer_class = RiskExposureSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class DecisionRuleViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = EnterpriseDecisionRule.objects.all()
    serializer_class = DecisionRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class LearningLoopViewSet(SystemicERPViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = LearningLoopRecord.objects.all()
    serializer_class = LearningLoopSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class AutonomousActionViewSet(SystemicERPViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = AutonomousActionRecord.objects.all()
    serializer_class = AutonomousActionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class CashProposalViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = CashOptimizationProposal.objects.all()
    serializer_class = CashProposalSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class SelfHealingViewSet(SystemicERPViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = SelfHealingAudit.objects.all()
    serializer_class = SelfHealingSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
