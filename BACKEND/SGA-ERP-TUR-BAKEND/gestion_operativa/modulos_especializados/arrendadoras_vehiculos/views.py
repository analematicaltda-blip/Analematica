# backend/apps/prestadores/mi_negocio/gestion_operativa/modulos_especializados/arrendadoras_vehiculos/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import VehiculoDeAlquiler, Alquiler
from .serializers import VehiculoDeAlquilerSerializer, AlquilerSerializer
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.permissions import IsOwner

class VehiculoDeAlquilerViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar la flota de vehículos de alquiler.
    """
    serializer_class = VehiculoDeAlquilerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return VehiculoDeAlquiler.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        serializer.save(perfil=self.request.user.perfil_prestador)

    @action(detail=True, methods=['post'])
    def marcar_como_disponible(self, request, pk=None):
        vehiculo = self.get_object()
        if not vehiculo.disponible:
            # Lógica adicional: verificar que no haya alquileres activos que lo impidan.
            activos = Alquiler.objects.filter(
                vehiculo=vehiculo,
                estado='activo',
                fecha_devolucion__gt=timezone.now()
            ).exists()
            if activos:
                return Response({'error': 'No se puede marcar como disponible, hay alquileres activos.'}, status=status.HTTP_400_BAD_REQUEST)

            vehiculo.disponible = True
            vehiculo.save()
            return Response({'status': 'Vehículo marcado como disponible.'})
        return Response({'status': 'El vehículo ya estaba disponible.'}, status=status.HTTP_400_BAD_REQUEST)

class AlquilerViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los alquileres de vehículos.
    """
    serializer_class = AlquilerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        # Un prestador solo ve los alquileres de su propia flota.
        return Alquiler.objects.filter(vehiculo__perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        # La validación en el serializer se encarga de verificar la pertenencia del vehículo.
        # Aquí se podría añadir lógica para verificar la disponibilidad del vehículo en las fechas solicitadas.
        vehiculo = serializer.validated_data['vehiculo']
        fecha_recogida = serializer.validated_data['fecha_recogida']
        fecha_devolucion = serializer.validated_data['fecha_devolucion']

        # Lógica de validación de solapamiento de fechas
        solapamientos = Alquiler.objects.filter(
            vehiculo=vehiculo,
            estado__in=['reservado', 'activo'],
            fecha_recogida__lt=fecha_devolucion,
            fecha_devolucion__gt=fecha_recogida
        ).exists()

        if solapamientos:
            raise serializers.ValidationError("El vehículo ya está reservado para las fechas seleccionadas.")

        serializer.save()

    @action(detail=True, methods=['post'], url_path='marcar-activo')
    def marcar_activo(self, request, pk=None):
        alquiler = self.get_object()
        if alquiler.estado == 'reservado':
            alquiler.estado = 'activo'
            alquiler.save()
            # La lógica en el modelo se encarga de marcar el vehículo como no disponible
            return Response(self.get_serializer(alquiler).data)
        return Response({'error': 'Solo se puede activar un alquiler que está "reservado".'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='marcar-finalizado')
    def marcar_finalizado(self, request, pk=None):
        alquiler = self.get_object()
        if alquiler.estado == 'activo':
            alquiler.estado = 'finalizado'
            alquiler.save()
            # La lógica en el modelo se encarga de volver a marcar el vehículo como disponible
            return Response(self.get_serializer(alquiler).data)
        return Response({'error': 'Solo se puede finalizar un alquiler que está "activo".'}, status=status.HTTP_400_BAD_REQUEST)
