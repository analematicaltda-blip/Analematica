from rest_framework import serializers
from django.apps import apps
from .domain.models import OperacionComercial
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.clientes.models import Cliente
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'email', 'telefono', 'tipo_cliente', 'limite_credito', 'perfil_ref_id']

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'is_active']

class OperacionSerializer(serializers.ModelSerializer):
    cliente = ClienteSerializer(read_only=True)
    productos = ProductoSerializer(many=True, read_only=True, source='items')

    class Meta:
        model = OperacionComercial
        fields = ['id', 'operation_type', 'total', 'status', 'cliente', 'productos', 'perfil_ref_id']
    
    def create(self, validated_data):
        validated_data['tenant'] = self.context['request'].tenant
        return super().create(validated_data)
