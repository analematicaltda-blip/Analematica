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
from ..serializers.provider_serializers import administrator
from rest_framework.exceptions import PermissionDenied

class TourismProviderViewSet(viewsets.ModelViewSet):
    http_method_names=['get','post','put','patch','head','options']
    queryset = TourismProvider.objects.all()
    serializer_class = TourismProviderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Cada dueño solo ve sus propios prestadores
        if administrator(self.request.user):
            return TourismProvider.objects.all()
        return TourismProvider.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        if not administrator(self.request.user) and self.request.user.role not in {'PRESTADOR','BUSINESS_OWNER','BUSINESS_ADMIN','ARTESANO'}:
            raise PermissionDenied('El alta empresarial requiere un rol empresarial autorizado.')
        # A locally declared RNT is an identifier, not evidence of official verification.
        serializer.save(owner=self.request.user,rnt_validated=False,rnt_last_sync=None)

    def perform_update(self,serializer):
        changed='rnt_number' in serializer.validated_data and serializer.validated_data['rnt_number']!=serializer.instance.rnt_number
        serializer.save(**({'rnt_validated':False,'rnt_last_sync':None} if changed else {}))

    @action(detail=True, methods=['get'], url_path='company-identity')
    def company_identity(self, request, pk=None):
        from ..services.company_identity import resolve_company
        provider=self.get_object()
        link=resolve_company(request.user,provider.pk)
        response=Response({'provider_id':str(link.provider_id),'company_id':str(link.tenant_id),
                           'administrator_user_id':link.administrator_id,
                           'valid_until':link.valid_until,'financial_activation':False})
        response['Cache-Control']='no-store'
        return response

    @action(detail=True, methods=['post'])
    def sync_rnt(self, request, pk=None):
        """
        Fuerza la sincronización manual con el Registro Nacional de Turismo.
        """
        provider=self.get_object()
        from ..services.rnt_integration import RNTIntegrationService
        return RNTIntegrationService.sync_provider(provider.pk)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Devuelve el perfil del prestador logueado.
        """
        provider = TourismProvider.objects.filter(owner=request.user).first()
        if not provider:
             return Response({"error": "No provider profile found"}, status=404)
        return Response(self.get_serializer(provider).data)

    @action(detail=False, methods=['post'], url_path='login-rnt', permission_classes=[permissions.AllowAny])
    def login_rnt(self, request):
        """
        Inicia sesión utilizando credenciales validadas del Registro Nacional de Turismo.
        """
        from ..services.rnt_integration import RNTIntegrationService
        return RNTIntegrationService.login_via_rnt(request.data.get('rnt_number'),None)

class BusinessProfileViewSet(viewsets.ModelViewSet):
    http_method_names=['get','post','put','patch','head','options']
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if administrator(self.request.user):return self.queryset.all()
        return self.queryset.filter(provider__owner=self.request.user)

class TourismServiceViewSet(viewsets.ModelViewSet):
    http_method_names=['get','post','put','patch','head','options']
    queryset = TourismService.objects.all()
    serializer_class = TourismServiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if administrator(self.request.user):return self.queryset.all()
        return self.queryset.filter(provider__owner=self.request.user)

class ReservationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if administrator(user):
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
        reservation=self.get_object()
        # Scoped lookup first; the service boundary refuses financial execution too.
        return TourismFinancialService.process_reservation_payment(reservation.pk)
