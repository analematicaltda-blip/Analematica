from rest_framework import serializers
from .models import OrganizadorEvento, Evento, Promocion
from ...modulos_genericos.productos_servicios.serializers import ProductSerializer
from ...modulos_genericos.productos_servicios.models import Product

class EventoSerializer(serializers.ModelSerializer):
    producto = ProductSerializer()

    class Meta:
        model = Evento
        fields = ('id', 'producto', 'fecha_inicio', 'fecha_fin', 'ubicacion', 'capacidad')

class OrganizadorEventoSerializer(serializers.ModelSerializer):
    eventos = EventoSerializer(many=True, read_only=True)

    class Meta:
        model = OrganizadorEvento
        fields = ('id', 'nombre', 'descripcion', 'eventos')
        read_only_fields = ('perfil',)

class PromocionSerializer(serializers.ModelSerializer):
    # Mostramos los IDs de los productos para facilitar la asignación en el frontend
    productos_aplicables = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all() # El queryset se ajustará en la vista
    )

    class Meta:
        model = Promocion
        fields = (
            'id', 'nombre', 'descripcion', 'fecha_inicio', 'fecha_fin',
            'tipo_descuento', 'valor_descuento', 'productos_aplicables', 'activa'
        )
        read_only_fields = ('perfil',)

    def validate(self, data):
        # Valida que los productos seleccionados pertenezcan al perfil del usuario
        if 'productos_aplicables' in data:
            perfil = self.context['request'].user.perfil_prestador
            for producto in data['productos_aplicables']:
                if producto.perfil != perfil:
                    raise serializers.ValidationError(
                        f"El producto '{producto.nombre}' no pertenece a este proveedor."
                    )
        return data
