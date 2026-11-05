# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/agencias_de_viajes/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import PaqueteTuristico, ReservaPaquete
from .serializers import PaqueteTuristicoSerializer, ReservaPaqueteSerializer
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions import IsOwner

class PaqueteTuristicoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar paquetes turísticos.
    """
    serializer_class = PaqueteTuristicoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Filtra los paquetes para que solo el prestador logueado pueda ver y gestionar los suyos
        return PaqueteTuristico.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        # Asigna el perfil del prestador logueado automáticamente al crear un nuevo paquete
        serializer.save(perfil=self.request.user.perfil_prestador)

    @action(detail=True, methods=['post'])
    def publicar(self, request, pk=None):
        """
        Acción para cambiar el estado de un paquete a 'publicado'.
        """
        paquete = self.get_object()
        if paquete.estado != 'publicado':
            paquete.estado = 'publicado'
            paquete.save()
            return Response({'status': 'Paquete publicado'}, status=status.HTTP_200_OK)
        return Response({'status': 'El paquete ya estaba publicado'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def archivar(self, request, pk=None):
        """
        Acción para cambiar el estado de un paquete a 'archivado'.
        """
        paquete = self.get_object()
        if paquete.estado != 'archivado':
            paquete.estado = 'archivado'
            paquete.save()
            return Response({'status': 'Paquete archivado'}, status=status.HTTP_200_OK)
        return Response({'status': 'El paquete ya estaba archivado'}, status=status.HTTP_400_BAD_REQUEST)


class ReservaPaqueteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las reservas de paquetes turísticos.
    """
    serializer_class = ReservaPaqueteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Un prestador solo puede ver las reservas de sus propios paquetes.
        return ReservaPaquete.objects.filter(paquete__perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        # La validación en el serializer se asegura de que el paquete pertenezca al prestador.
        serializer.save()
