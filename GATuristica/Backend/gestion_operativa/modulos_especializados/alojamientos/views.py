from rest_framework import viewsets, permissions, views, status
from rest_framework.response import Response
from django.utils.dateparse import parse_date
from .models import TipoAlojamiento, Alojamiento, Habitacion, Tarifa
from .serializers import TipoAlojamientoSerializer, AlojamientoSerializer, HabitacionSerializer, TarifaSerializer
from apps.prestadores.mi_negocio.permissions import IsPrestadorOwner
from ...modulos_genericos.reservas.models import Reserva

class TipoAlojamientoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para ver los tipos de alojamiento disponibles.
    """
    queryset = TipoAlojamiento.objects.all()
    serializer_class = TipoAlojamientoSerializer
    permission_classes = [permissions.IsAuthenticated]

class AlojamientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para que un proveedor gestione su Alojamiento.
    """
    serializer_class = AlojamientoSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        return Alojamiento.objects.filter(perfil=self.request.user.perfil_prestador)

    def perform_create(self, serializer):
        # Asegurarse de que un perfil solo tenga un alojamiento
        if Alojamiento.objects.filter(perfil=self.request.user.perfil_prestador).exists():
            raise serializers.ValidationError("El perfil ya tiene un alojamiento asociado.")
        serializer.save(perfil=self.request.user.perfil_prestador)

class HabitacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las habitaciones de un Alojamiento.
    """
    serializer_class = HabitacionSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        # El usuario solo puede ver habitaciones de su propio alojamiento
        try:
            alojamiento = self.request.user.perfil_prestador.alojamiento
            return Habitacion.objects.filter(alojamiento=alojamiento)
        except Alojamiento.DoesNotExist:
            return Habitacion.objects.none()

class TarifaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las tarifas de una Habitación.
    """
    serializer_class = TarifaSerializer
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get_queryset(self):
        # Filtra tarifas de habitaciones que pertenecen al alojamiento del usuario
        try:
            alojamiento = self.request.user.perfil_prestador.alojamiento
            return Tarifa.objects.filter(habitacion__alojamiento=alojamiento)
        except Alojamiento.DoesNotExist:
            return Tarifa.objects.none()

class CalendarioDisponibilidadView(views.APIView):
    """
    Vista para obtener la disponibilidad de todas las habitaciones de un alojamiento
    en un rango de fechas.
    """
    permission_classes = [permissions.IsAuthenticated, IsPrestadorOwner]

    def get(self, request, *args, **kwargs):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if not start_date_str or not end_date_str:
            return Response(
                {"error": "Los parámetros 'start_date' y 'end_date' son requeridos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        if not start_date or not end_date or start_date > end_date:
            return Response(
                {"error": "Formato de fecha inválido o rango incorrecto."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            alojamiento = request.user.perfil_prestador.alojamiento
        except Alojamiento.DoesNotExist:
            return Response({"error": "No se encontró un alojamiento para este perfil."}, status=status.HTTP_404_NOT_FOUND)

        habitaciones = Habitacion.objects.filter(alojamiento=alojamiento)

        # Obtener reservas confirmadas que se solapan con el rango de fechas
        reservas = Reserva.objects.filter(
            producto__in=habitaciones.values('producto'),
            estado='confirmada',
            fecha_inicio__lte=end_date,
            fecha_fin__gte=start_date
        ).values('producto_id', 'fecha_inicio', 'fecha_fin', 'id')

        # Estructurar la respuesta
        calendario = {}
        for habitacion in habitaciones:
            calendario[habitacion.id] = {
                "nombre_habitacion": habitacion.producto.nombre,
                "reservas": []
            }

        for reserva in reservas:
            # Buscamos la habitación que corresponde al producto de la reserva
            habitacion_id = habitaciones.get(producto_id=reserva['producto_id']).id
            if habitacion_id in calendario:
                 calendario[habitacion_id]['reservas'].append({
                     'reserva_id': reserva['id'],
                     'start': reserva['fecha_inicio'],
                     'end': reserva['fecha_fin']
                 })

        return Response(calendario)
