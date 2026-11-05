from rest_framework import serializers
from .models import TipoAlojamiento, Alojamiento, Habitacion, Tarifa
from ...modulos_genericos.productos_servicios.serializers import ProductSerializer

class TipoAlojamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAlojamiento
        fields = '__all__'

class TarifaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarifa
        fields = ('id', 'nombre', 'fecha_inicio', 'fecha_fin', 'precio_adicional')

class HabitacionSerializer(serializers.ModelSerializer):
    tarifas = TarifaSerializer(many=True, read_only=True)
    # Reutilizamos el ProductSerializer para obtener los detalles del producto base
    producto = ProductSerializer()

    class Meta:
        model = Habitacion
        fields = ('id', 'producto', 'capacidad_maxima', 'tarifas')

class AlojamientoSerializer(serializers.ModelSerializer):
    habitaciones = HabitacionSerializer(many=True, read_only=True)
    tipo = serializers.StringRelatedField() # Muestra el nombre en lugar del ID

    class Meta:
        model = Alojamiento
        fields = ('id', 'tipo', 'nombre', 'descripcion', 'direccion', 'habitaciones')
        read_only_fields = ('perfil',)
