from rest_framework import viewsets, permissions
from apps.admin_plataforma.gestion_contable.nomina.models import (
    Employee, EmploymentContract, PayrollRun, PayrollConcept
)
from .serializers import (
    EmployeeSerializer, EmploymentContractSerializer,
    PayrollRunSerializer, PayrollConceptSerializer
)
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from api.permissions import IsSuperAdmin

class EmployeeViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.all() # Automatically filtered by TenantManager
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class EmploymentContractViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = EmploymentContract.objects.all()
    serializer_class = EmploymentContractSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class PayrollRunViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

class PayrollConceptViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PayrollConcept.objects.all()
    serializer_class = PayrollConceptSerializer
    permission_classes = [permissions.IsAuthenticated]
