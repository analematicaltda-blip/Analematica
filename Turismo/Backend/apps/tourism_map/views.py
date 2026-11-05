from rest_framework import serializers, viewsets
from .models import TourismLocation

class TourismLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourismLocation
        fields = '__all__'

class TourismLocationViewSet(viewsets.ModelViewSet):
    """
    API para el Mapa Turístico Inteligente.
    """
    queryset = TourismLocation.objects.all()
    serializer_class = TourismLocationSerializer
    filterset_fields = ['type', 'city']
    search_fields = ['name', 'description']
