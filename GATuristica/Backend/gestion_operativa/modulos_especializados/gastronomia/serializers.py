from rest_framework import serializers
from .models import Restaurante, Menu, CategoriaPlato, Plato, ZonaDelivery
from ...modulos_genericos.productos_servicios.serializers import ProductSerializer

class ZonaDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = ZonaDelivery
        fields = ('id', 'nombre', 'costo_envio', 'tiempo_estimado_minutos')

class PlatoSerializer(serializers.ModelSerializer):
    # Usamos el ProductSerializer para obtener los detalles del producto base
    producto = ProductSerializer()

    class Meta:
        model = Plato
        fields = ('id', 'producto', 'disponible')

class CategoriaPlatoSerializer(serializers.ModelSerializer):
    platos = PlatoSerializer(many=True, read_only=True)

    class Meta:
        model = CategoriaPlato
        fields = ('id', 'nombre', 'orden', 'platos')

class MenuSerializer(serializers.ModelSerializer):
    categorias = CategoriaPlatoSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ('id', 'nombre', 'descripcion', 'activo', 'categorias')

class RestauranteSerializer(serializers.ModelSerializer):
    menus = MenuSerializer(many=True, read_only=True)
    zonas_delivery = ZonaDeliverySerializer(many=True, read_only=True)

    class Meta:
        model = Restaurante
        fields = ('id', 'nombre', 'descripcion', 'ofrece_delivery', 'menus', 'zonas_delivery')
        read_only_fields = ('perfil',)
