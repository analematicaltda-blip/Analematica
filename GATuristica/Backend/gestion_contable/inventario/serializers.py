from rest_framework import serializers
from .models import Almacen, MovimientoInventario

class AlmacenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Almacen
        fields = ['id', 'nombre', 'ubicacion']

    def create(self, validated_data):
        validated_data['perfil'] = self.context['request'].user.perfil_prestador
        return super().create(validated_data)

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    usuario = serializers.HiddenField(default=serializers.CurrentUserDefault())
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    almacen_nombre = serializers.CharField(source='almacen.nombre', read_only=True)

    class Meta:
        model = MovimientoInventario
        fields = [
            'id', 'producto', 'producto_nombre', 'almacen', 'almacen_nombre',
            'tipo_movimiento', 'cantidad', 'fecha', 'descripcion', 'usuario'
        ]
        read_only_fields = ('fecha',)
