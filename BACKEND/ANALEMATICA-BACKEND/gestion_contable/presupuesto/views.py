from rest_framework import viewsets, permissions
from .models import Budget, BudgetItem, BudgetExecution
from .serializers import BudgetSerializer, BudgetItemSerializer, BudgetExecutionSerializer
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class BudgetViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class BudgetItemViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = BudgetItem.objects.all()
    serializer_class = BudgetItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class BudgetExecutionViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = BudgetExecution.objects.all()
    serializer_class = BudgetExecutionSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]
