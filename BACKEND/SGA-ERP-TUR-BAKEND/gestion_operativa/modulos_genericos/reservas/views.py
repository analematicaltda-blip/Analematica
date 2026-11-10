from rest_framework import viewsets, permissions
from .models import Reserva, PoliticaCancelacion
from .serializers import ReservaSerializer, PoliticaCancelacionSerializer
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner

class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        """
        El proveedor solo puede ver sus propias reservas.
        """
        return Reserva.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        """
        Asigna el perfil del proveedor automáticamente al crear una reserva.
        """
        serializer.save(perfil=self.request.user.perfil_prestador)

class PoliticaCancelacionViewSet(viewsets.ModelViewSet):
    """Legacy descriptions remain scoped; managed percentages use immutable versions."""
    from rest_framework_simplejwt.authentication import JWTAuthentication
    from ....web_session import ErpSessionAuthentication
    authentication_classes=[JWTAuthentication,ErpSessionAuthentication]
    serializer_class=PoliticaCancelacionSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_queryset(self):
        from ....company_scope import owned_provider
        return PoliticaCancelacion.objects.filter(perfil_ref_id=owned_provider(self.request).pk)

    def perform_create(self,serializer):
        from ....company_scope import owned_provider
        serializer.save(perfil_ref_id=owned_provider(self.request).pk)

    def protected(self,instance):
        from apps.core_erp.outbox_models import OutboxEvent
        from rest_framework.exceptions import ValidationError
        if OutboxEvent.objects.filter(event_type='commercial.cancellation-policy.published.v1',payload__provider_id=str(instance.perfil_ref_id),payload__body__policy_id=instance.pk).exists():raise ValidationError('Política versionada: publica una revisión desde el panel; no se modifica ni elimina su evidencia.')

    def perform_update(self,serializer):
        from django.db import transaction
        with transaction.atomic():
            row=self.get_queryset().select_for_update().get(pk=serializer.instance.pk);self.protected(row);serializer.instance=row;serializer.save()

    def perform_destroy(self,instance):
        from django.db import transaction
        with transaction.atomic():
            row=self.get_queryset().select_for_update().get(pk=instance.pk);self.protected(row);row.delete()
