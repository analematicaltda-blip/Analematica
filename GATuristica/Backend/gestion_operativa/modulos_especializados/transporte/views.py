from rest_framework import viewsets
from .models import Vehicle #, MaintenanceOrder
from .serializers import VehicleSerializer #, MaintenanceOrderSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    filterset_fields = ['status', 'tipo_vehiculo']
    search_fields = ['nombre', 'placa']

# class MaintenanceOrderViewSet(viewsets.ModelViewSet):
#     queryset = MaintenanceOrder.objects.all()
#     serializer_class = MaintenanceOrderSerializer
#     filterset_fields = ['vehicle', 'maintenance_type']

# La acción para asignar recursos (vehículo, conductor) a una reserva
# se implementará en el `ReservationViewSet` del módulo genérico 'reservas'.
#
# @action(detail=True, methods=['post'], url_path='assign-transport')
# def assign_transport(self, request, pk=None):
#     reservation = self.get_object()
#     vehicle_id = request.data.get('vehicle_id')
#     driver_id = request.data.get('driver_id')
#     # ... lógica de asignación y validación ...
#     return Response(...)
