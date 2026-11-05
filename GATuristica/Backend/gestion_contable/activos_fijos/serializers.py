from rest_framework import serializers
from .models import CategoriaActivo, ActivoFijo, CalculoDepreciacion
from apps.common.serializers.polymorphic_owner import PolymorphicOwnerSerializerMixin

class CategoriaActivoSerializer(PolymorphicOwnerSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = CategoriaActivo
        fields = ['id', 'nombre', 'descripcion', 'owner', 'owner_details']

class ActivoFijoSerializer(PolymorphicOwnerSerializerMixin, serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)

    class Meta:
        model = ActivoFijo
        fields = [
            'id', 'nombre', 'categoria', 'categoria_nombre', 'descripcion', 'fecha_adquisicion',
            'costo_adquisicion', 'valor_residual', 'vida_util_meses', 'metodo_depreciacion',
            'depreciacion_acumulada', 'valor_en_libros', 'owner', 'owner_details'
        ]
        read_only_fields = ('depreciacion_acumulada', 'valor_en_libros')

class CalculoDepreciacionSerializer(serializers.ModelSerializer):
    creado_por = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = CalculoDepreciacion
        fields = ['id', 'activo', 'fecha', 'monto', 'creado_por', 'creado_en']
        read_only_fields = ('creado_en',)
