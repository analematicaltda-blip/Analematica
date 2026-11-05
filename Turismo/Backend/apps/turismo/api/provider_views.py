from django.db import models
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.provider_models import TourismProvider, BusinessProfile, TourismService, Reservation
from ..serializers.provider_serializers import (
    TourismProviderSerializer, BusinessProfileSerializer,
    TourismServiceSerializer, ReservationSerializer
)
from ..services.financial_service import TourismFinancialService

class TourismProviderViewSet(viewsets.ModelViewSet):
    queryset = TourismProvider.objects.all()
    serializer_class = TourismProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada dueño solo ve sus propios prestadores
        if self.request.user.is_staff:
            return TourismProvider.objects.all()
        return TourismProvider.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        provider = serializer.save(owner=self.request.user)
        # Sincronización automática con RNT si se proveyó número
        if provider.rnt_number:
            from ..services.rnt_integration import RNTIntegrationService
            RNTIntegrationService.sync_provider(provider.id)

    @action(detail=True, methods=['post'])
    def sync_rnt(self, request, pk=None):
        """
        Fuerza la sincronización manual con el Registro Nacional de Turismo.
        """
        from ..services.rnt_integration import RNTIntegrationService
        success = RNTIntegrationService.sync_provider(pk)
        if success:
            return Response({"status": "success", "message": "Datos sincronizados con éxito."})
        return Response({"status": "error", "message": "No se pudo validar el RNT."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Devuelve el perfil del prestador logueado.
        """
        provider = TourismProvider.objects.filter(owner=request.user).first()
        if not provider:
             return Response({"error": "No provider profile found"}, status=404)
        return Response(TourismProviderSerializer(provider).data)

    @action(detail=False, methods=['post'], url_path='login-rnt', permission_classes=[permissions.AllowAny])
    def login_rnt(self, request):
        """
        Inicia sesión utilizando credenciales validadas del Registro Nacional de Turismo.
        """
        rnt_number = request.data.get('rnt_number')
        # password_token = request.data.get('rnt_token') # En producción

        from ..services.rnt_integration import RNTIntegrationService
        user = RNTIntegrationService.login_via_rnt(rnt_number, None)

        if user:
            # Aquí se retornaría un JWT real
            return Response({
                "status": "success",
                "message": f"Acceso concedido para RNT {rnt_number}",
                "user": user.username
            })
        return Response({"error": "Credenciales RNT inválidas o prestador no registrado."}, status=status.HTTP_401_UNAUTHORIZED)

class BusinessProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class TourismServiceViewSet(viewsets.ModelViewSet):
    queryset = TourismService.objects.all()
    serializer_class = TourismServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        # Turista ve sus reservas, Dueño ve las reservas de sus prestadores
        return Reservation.objects.filter(
            models.Q(customer=user) | models.Q(provider__owner=user)
        ).distinct()

    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """
        Inicia el flujo de pago de la reserva.
        """
        try:
            result = TourismFinancialService.process_reservation_payment(pk)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
