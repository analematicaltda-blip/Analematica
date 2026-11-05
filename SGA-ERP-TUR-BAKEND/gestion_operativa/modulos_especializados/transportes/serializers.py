from rest_framework import serializers
from .models import CompaniaTransporte, TipoVehiculo, Vehiculo, Ruta, HorarioRuta
from ...modulos_genericos.productos_servicios.serializers import ProductSerializer

class TipoVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoVehiculo
        fields = '__all__'

class VehiculoSerializer(serializers.ModelSerializer):
    producto = ProductSerializer()
    tipo = serializers.StringRelatedField()

    class Meta:
        model = Vehiculo
        fields = ('id', 'producto', 'tipo', 'placa', 'capacidad_pasajeros')

class HorarioRutaSerializer(serializers.ModelSerializer):
    vehiculo = serializers.StringRelatedField()

    class Meta:
        model = HorarioRuta
        fields = ('id', 'vehiculo', 'hora_salida', 'hora_llegada_estimada', 'dias_operacion')

class RutaSerializer(serializers.ModelSerializer):
    horarios = HorarioRutaSerializer(many=True, read_only=True)

    class Meta:
        model = Ruta
        fields = ('id', 'nombre', 'origen', 'destino', 'distancia_km', 'horarios')

class CompaniaTransporteSerializer(serializers.ModelSerializer):
    vehiculos = VehiculoSerializer(many=True, read_only=True)
    rutas = RutaSerializer(many=True, read_only=True)

    class Meta:
        model = CompaniaTransporte
        fields = ('id', 'nombre', 'descripcion', 'vehiculos', 'rutas')
        read_only_fields = ('perfil',)
