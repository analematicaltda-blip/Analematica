from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Amenity, RoomType, Room
from .serializers import AmenitySerializer, RoomTypeSerializer, RoomSerializer
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.perfil.models import TenantAwareModel # Para permisos

class HotelFeatureViewSet(viewsets.ModelViewSet):
    """
    ViewSet base para características de hotel que solo pertenecen al proveedor.
    El TenantManager se encarga del aislamiento.
    """
    filter_backends = [DjangoFilterBackend]
    # permission_classes = [IsAuthenticated] # Se hereda de DRF por defecto

class AmenityViewSet(HotelFeatureViewSet):
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer

class RoomTypeViewSet(HotelFeatureViewSet):
    queryset = RoomType.objects.select_related('product').prefetch_related('amenities').all()
    serializer_class = RoomTypeSerializer

class RoomViewSet(HotelFeatureViewSet):
    queryset = Room.objects.select_related('room_type__product').all()
    serializer_class = RoomSerializer
    filterset_fields = ['room_type', 'housekeeping_status']
