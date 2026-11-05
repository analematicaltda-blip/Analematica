from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DeliveryCompany, Driver, Vehicle, DeliveryService, DeliveryEvent, Ruta, IndicadorLogistico
from .serializers import (
    DeliveryCompanySerializer, DriverSerializer, VehicleSerializer,
    DeliveryServiceSerializer, DeliveryEventSerializer, RutaSerializer, IndicadorLogisticoSerializer
)
from apps.admin_plataforma.services.governance_kernel import GovernanceKernel
from .services import DeliveryLogisticService
from django.db.models import Sum, Count, Avg
from django.utils import timezone

class DeliveryCompanyViewSet(viewsets.ModelViewSet):
    queryset = DeliveryCompany.objects.all()
    serializer_class = DeliveryCompanySerializer
    permission_classes = [permissions.IsAuthenticated]

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticated]

class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer
    permission_classes = [permissions.IsAuthenticated]

class DeliveryServiceViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return DeliveryService.objects.all()

        # Check if user has any delivery-related role
        is_delivery_role = user.role in ['DELIVERY', 'DELIVERY_ADMIN', 'DELIVERY_DRIVER', 'DELIVERY_OPERATOR']

        if user.role == 'TURISTA':
            return DeliveryService.objects.filter(tourist_id=user.id)
        if is_delivery_role or user.role == 'PRESTADOR':
            return DeliveryService.objects.all() # For visibility in dashboards
        return DeliveryService.objects.none()

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """ Resumen ejecutivo de Delivery """
        pedidos = DeliveryService.objects.all()
        data = {
            "total_pedidos": pedidos.count(),
            "en_ruta": pedidos.filter(status='EN_RUTA').count(),
            "entregados": pedidos.filter(status='ENTREGADO').count(),
            "fallidos": pedidos.filter(status='FALLIDO').count(),
            "repartidores_activos": Driver.objects.filter(is_available=True).count()
        }
        return Response(data)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        service = DeliveryLogisticService(user=request.user)
        try:
            res = service.assign_service(pk, driver_id=request.data.get("driver_id"))
            return Response(DeliveryServiceSerializer(res).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        service = DeliveryLogisticService(user=request.user)
        res = service.start_delivery(pk)
        return Response(DeliveryServiceSerializer(res).data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        service = DeliveryLogisticService(user=request.user)
        try:
            res = service.complete_service(pk, parameters=request.data)
            return Response(DeliveryServiceSerializer(res).data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def fail(self, request, pk=None):
        service = DeliveryLogisticService(user=request.user)
        res = service.fail_delivery(pk, request.data.get("reason", "No especificado"))
        return Response(DeliveryServiceSerializer(res).data)

class IndicadorLogisticoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IndicadorLogistico.objects.all()
    serializer_class = IndicadorLogisticoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        provider_id = request.data.get("provider_id")
        DeliveryLogisticService.generar_indicadores(provider_id)
        return Response({"status": "KPIs recalculados"})
