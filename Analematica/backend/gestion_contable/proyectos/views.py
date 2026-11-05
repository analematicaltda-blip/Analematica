from rest_framework import viewsets, permissions
from .models import Project, ProjectIncome, ProjectCost
from .serializers import ProjectSerializer, ProjectIncomeSerializer, ProjectCostSerializer
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class ProjectViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ProjectIncomeViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = ProjectIncome.objects.all()
    serializer_class = ProjectIncomeSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class ProjectCostViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = ProjectCost.objects.all()
    serializer_class = ProjectCostSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
