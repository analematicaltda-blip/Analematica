from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from ..domain.models import OperacionComercial, ItemOperacionComercial, FacturaVenta, ItemFactura, ReciboCaja
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.serializers import ClienteSerializer
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product

class ItemOperacionComercialSerializer(serializers.ModelSerializer):
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='producto'
    )

    class Meta:
        model = ItemOperacionComercial
        fields = ['producto_id', 'descripcion', 'cantidad', 'precio_unitario']

class OperacionComercialSerializer(serializers.ModelSerializer):
    items = ItemOperacionComercialSerializer(many=True)
    cliente_id = serializers.PrimaryKeyRelatedField(
        queryset=Cliente.objects.all(), source='cliente'
    )
    estado = serializers.CharField(read_only=True)

    class Meta:
        model = OperacionComercial
        fields = ['id', 'cliente_id', 'tipo_operacion', 'estado', 'subtotal', 'impuestos', 'total', 'items']
        read_only_fields = ('subtotal', 'impuestos', 'total')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['perfil'] = self.context['request'].user.perfil_prestador
        validated_data['creado_por'] = self.context['request'].user

        operacion = OperacionComercial.objects.create(**validated_data)
        for item_data in items_data:
            ItemOperacionComercial.objects.create(operacion=operacion, **item_data)

        operacion.recalcular_totales()
        return operacion


class ItemFacturaSerializer(serializers.ModelSerializer):
    producto_id = serializers.UUIDField(source='producto_ref_id')

    class Meta:
        model = ItemFactura
        fields = ['id', 'producto_id', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal', 'impuestos']
        read_only_fields = ('subtotal',)

class FacturaVentaListSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    estado_display = serializers.CharField(source='operacion.get_estado_display', read_only=True)
    total = serializers.DecimalField(source='operacion.total', max_digits=12, decimal_places=2, read_only=True)

    @extend_schema_field(serializers.ChoiceField(choices=OperacionComercial.Estado.choices))
    def get_estado(self, obj):
        return obj.operacion.estado

    estado = serializers.SerializerMethodField()

    class Meta:
        model = FacturaVenta
        fields = ['id', 'number', 'cliente_nombre', 'issue_date', 'total', 'estado', 'estado_display']
        read_only_fields = fields

class FacturaVentaDetailSerializer(serializers.ModelSerializer):
    items = ItemFacturaSerializer(many=True, read_only=True)
    cliente = ClienteSerializer(read_only=True)
    estado_display = serializers.CharField(source='operacion.get_estado_display', read_only=True)
    total = serializers.DecimalField(source='operacion.total', max_digits=12, decimal_places=2, read_only=True)

    @extend_schema_field(serializers.ChoiceField(choices=OperacionComercial.Estado.choices))
    def get_estado(self, obj):
        return obj.operacion.estado

    estado = serializers.SerializerMethodField()

    subtotal = serializers.DecimalField(source='operacion.subtotal', max_digits=12, decimal_places=2, read_only=True)
    impuestos = serializers.DecimalField(source='operacion.impuestos', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = FacturaVenta
        fields = [
            'id', 'number', 'cliente', 'issue_date',
            'subtotal', 'impuestos', 'total',
            'estado', 'estado_display', 'items'
        ]
        read_only_fields = fields


class FacturaVentaWriteSerializer(serializers.ModelSerializer):
    items = ItemFacturaSerializer(many=True, required=False)
    creado_por = serializers.HiddenField(default=serializers.CurrentUserDefault())
    cliente_id = serializers.UUIDField(write_only=True, required=True)
    total = serializers.DecimalField(source='operacion.total', max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = FacturaVenta
        fields = [
            'id', 'cliente_id', 'number', 'issue_date',
            'operacion', 'creado_por', 'items', 'total'
        ]
        read_only_fields = ('total',)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        usuario = self.context['request'].user
        perfil_id = usuario.perfil_prestador.id
        cliente_id = validated_data.get('cliente_id')

        # Usar el servicio para procesar la intención comercial gobernada
        from ..services import FacturacionService
        operacion = FacturacionService.procesar_intencion_venta(
            perfil_id=perfil_id,
            cliente_id=cliente_id,
            items_data=items_data,
            usuario=usuario
        )

        # La factura se crea como consecuencia de la confirmación de la operación (o por el agente)
        # En este flujo síncrono para la UI, forzamos la creación de la factura si la operación se creó.
        # En una fase más avanzada, esto sería asíncrono tras la firma del contrato.
        factura = FacturacionService.facturar_operacion_confirmada(operacion)
        return factura


class ReciboCajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReciboCaja
        fields = ['id', 'factura', 'cuenta_bancaria', 'fecha_pago', 'monto', 'metodo_pago']

    def create(self, validated_data):
        validated_data['perfil'] = self.context['request'].user.perfil_prestador
        recibo = ReciboCaja.objects.create(**validated_data)
        return recibo
