from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import KitchenStation, RestaurantTable
from .serializers import KitchenStationSerializer, RestaurantTableSerializer

class KitchenStationViewSet(viewsets.ModelViewSet):
    queryset = KitchenStation.objects.all()
    serializer_class = KitchenStationSerializer

class RestaurantTableViewSet(viewsets.ModelViewSet):
    queryset = RestaurantTable.objects.all()
    serializer_class = RestaurantTableSerializer

    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        table = self.get_object()
        new_status = request.data.get('status')
        if not new_status or new_status not in RestaurantTable.TableStatus.values:
            return Response({'error': 'Estado no válido.'}, status=status.HTTP_400_BAD_REQUEST)

        table.status = new_status
        table.save()
        # Aquí se podría disparar una notificación de WebSocket
        return Response(self.get_serializer(table).data)

    @action(detail=False, methods=['post'], url_path='update-positions')
    def update_positions(self, request):
        """
        Recibe una lista de mesas con sus nuevas coordenadas y las actualiza en lote.
        """
        updates = request.data.get('updates', [])
        for update in updates:
            RestaurantTable.objects.filter(id=update['id']).update(pos_x=update['pos_x'], pos_y=update['pos_y'])
        return Response(status=status.HTTP_204_NO_CONTENT)

# Los ViewSets para Order y OrderItem se implementarán en la fase de 'Módulos Genéricos'
# pero su lógica será crucial para el módulo de restaurante.
