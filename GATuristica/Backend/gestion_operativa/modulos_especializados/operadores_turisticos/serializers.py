from rest_framework import serializers
from .models import OperadorTuristico, PaqueteTuristico, ItinerarioDia
from ...modulos_genericos.productos_servicios.serializers import ProductSerializer

class ItinerarioDiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItinerarioDia
        fields = ('dia', 'titulo', 'descripcion')

class PaqueteTuristicoSerializer(serializers.ModelSerializer):
    producto = ProductSerializer()
    itinerario = ItinerarioDiaSerializer(many=True, read_only=True)

    class Meta:
        model = PaqueteTuristico
        fields = ('id', 'producto', 'duracion_dias', 'incluye', 'itinerario')

class OperadorTuristicoSerializer(serializers.ModelSerializer):
    paquetes = PaqueteTuristicoSerializer(many=True, read_only=True)

    class Meta:
        model = OperadorTuristico
        fields = ('id', 'nombre', 'descripcion', 'licencia_turismo', 'paquetes')
        read_only_fields = ('perfil',)
