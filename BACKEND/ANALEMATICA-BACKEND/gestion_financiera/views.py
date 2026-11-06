from rest_framework import viewsets, permissions
from api.permissions import IsSuperAdmin
from apps.admin_plataforma.mixins import SystemicERPViewSetMixin
from apps.admin_plataforma.gestion_financiera.models import CuentaBancaria, OrdenPago
from .serializers import AdminCuentaBancariaSerializer, AdminOrdenPagoSerializer
from apps.core_erp.treasury_engine import TreasuryEngine

class CuentaBancariaViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = CuentaBancaria.objects.all()
    serializer_class = AdminCuentaBancariaSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    def perform_create(self, serializer):
        from apps.admin_plataforma.services.gestion_plataforma_service import GestionPlataformaService
        perfil_gobierno = GestionPlataformaService.get_perfil_gobierno()
        serializer.save(perfil_ref_id=perfil_gobierno.id)

class OrdenPagoViewSet(SystemicERPViewSetMixin, viewsets.ModelViewSet):
    queryset = OrdenPago.objects.all()
    serializer_class = AdminOrdenPagoSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdmin]

    def perform_create(self, serializer):
        orden = serializer.save()
        # TreasuryEngine.apply_payment(orden, orden.amount, ...)
        # Nota: Aquí se dispara la lógica del motor de tesorería
