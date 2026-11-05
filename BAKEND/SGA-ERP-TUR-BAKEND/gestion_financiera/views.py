from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import CuentaBancaria, OrdenPago, TesoreriaCentral, EstadoResultados, BalanceGeneral, FlujoEfectivo, CambiosPatrimonio, ReservaFinanciera, ProyeccionFinanciera, RiesgoFinanciero
from .serializers import *
from .sargentos import SargentoFinanciero

class IsPrestadorOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return str(obj.perfil_ref_id) == str(request.user.perfil_prestador.id)

class CuentaBancariaViewSet(viewsets.ModelViewSet):
    serializer_class = CuentaBancariaSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil_prestador'):
            return CuentaBancaria.objects.filter(perfil_ref_id=self.request.user.perfil_prestador.id)
        return CuentaBancaria.objects.none()

class OrdenPagoViewSet(viewsets.ModelViewSet):
    serializer_class = OrdenPagoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        if hasattr(self.request.user, 'perfil_prestador'):
            return OrdenPago.objects.filter(perfil_ref_id=self.request.user.perfil_prestador.id)
        return OrdenPago.objects.none()

    @action(detail=True, methods=['post'])
    def ejecutar(self, request, pk=None):
        try:
            resultado = SargentoFinanciero.ejecutar_pago(pk, request.user.id)
            return Response(resultado)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TesoreriaCentralViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TesoreriaCentralSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TesoreriaCentral.objects.filter(provider_id=self.request.user.perfil_prestador.id)

class EstadoResultadosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EstadoResultadosSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return EstadoResultados.objects.filter(provider_id=self.request.user.perfil_prestador.id)

class BalanceGeneralViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BalanceGeneralSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return BalanceGeneral.objects.filter(provider_id=self.request.user.perfil_prestador.id)

class ProyeccionFinancieraViewSet(viewsets.ModelViewSet):
    serializer_class = ProyeccionFinancieraSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return ProyeccionFinanciera.objects.filter(provider_id=self.request.user.perfil_prestador.id)

class RiesgoFinancieroViewSet(viewsets.ModelViewSet):
    serializer_class = RiesgoFinancieroSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return RiesgoFinanciero.objects.filter(provider_id=self.request.user.perfil_prestador.id)

class PresupuestoViewSet(viewsets.ModelViewSet):
    serializer_class = PresupuestoSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Presupuesto.objects.filter(provider_id=self.request.user.perfil_prestador.id)

class CreditoFinancieroViewSet(viewsets.ModelViewSet):
    serializer_class = CreditoFinancieroSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return CreditoFinanciero.objects.filter(provider_id=self.request.user.perfil_prestador.id)

class IndicadorFinancieroViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IndicadorFinancieroHistoricoSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return IndicadorFinancieroHistorico.objects.filter(provider_id=self.request.user.perfil_prestador.id)

class AlertaFinancieraViewSet(viewsets.ModelViewSet):
    serializer_class = AlertaFinancieraSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return AlertaFinanciera.objects.filter(provider_id=self.request.user.perfil_prestador.id)

    @action(detail=True, methods=['post'])
    def resolver(self, request, pk=None):
        alerta = self.get_object()
        alerta.resuelta = True
        alerta.save()
        return Response({"status": "Alerta resuelta"})

class LogFinancieroViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LogFinancieroInmutableSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return LogFinancieroInmutable.objects.filter(provider_id=self.request.user.perfil_prestador.id)
