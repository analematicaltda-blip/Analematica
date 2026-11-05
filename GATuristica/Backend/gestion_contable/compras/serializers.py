from rest_framework import serializers
from .models import Proveedor, FacturaCompra

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'identificacion', 'telefono', 'email', 'direccion']

    def create(self, validated_data):
        validated_data['perfil'] = self.context['request'].user.perfil_prestador
        return super().create(validated_data)

class FacturaCompraSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True)
    creado_por = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = FacturaCompra
        fields = [
            'id', 'proveedor', 'proveedor_nombre', 'number', 'issue_date',
            'fecha_vencimiento', 'subtotal', 'impuestos', 'total', 'estado',
            'notas', 'creado_por', 'creado_en'
        ]
        read_only_fields = ('creado_en',)
        extra_kwargs = {
            'proveedor': {'write_only': True}
        }

    def validate(self, data):
        """
        Verifica que no exista otra factura con el mismo número para el mismo proveedor.
        La validación se aplica solo en la creación de una nueva factura.
        """
        # La validación se aplica solo en la creación (POST)
        if not self.instance:
            proveedor = data.get('proveedor')
            number = data.get('number')
            perfil = self.context['request'].user.perfil_prestador

            if FacturaCompra.objects.filter(
                perfil=perfil,
                proveedor=proveedor,
                number=number
            ).exists():
                raise serializers.ValidationError(
                    f"Ya existe una factura con el número '{number}' para este proveedor."
                )
        return data

    def create(self, validated_data):
        validated_data['perfil'] = self.context['request'].user.perfil_prestador
        return super().create(validated_data)
