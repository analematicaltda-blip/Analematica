from rest_framework import serializers
from .models import Proyecto, IngresoProyecto, CostoProyecto

class IngresoProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngresoProyecto
        fields = ['id', 'descripcion', 'monto', 'fecha', 'factura']

class CostoProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostoProyecto
        fields = ['id', 'descripcion', 'monto', 'fecha', 'factura_compra']

class ProyectoSerializer(serializers.ModelSerializer):
    ingresos = IngresoProyectoSerializer(many=True, read_only=True)
    costos = CostoProyectoSerializer(many=True, read_only=True)
    total_ingresos = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_costos = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    rentabilidad = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Proyecto
        fields = [
            'id', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'presupuesto',
            'estado', 'ingresos', 'costos', 'total_ingresos', 'total_costos', 'rentabilidad'
        ]

    def create(self, validated_data):
        validated_data['perfil'] = self.context['request'].user.perfil_prestador
        return super().create(validated_data)
