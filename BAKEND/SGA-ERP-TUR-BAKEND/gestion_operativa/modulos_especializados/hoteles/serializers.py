from rest_framework import serializers
from .models import Amenity, RoomType, Room
from apps.prestadores.mi_negocio.gestion_operativa.modulos_genericos.productos_servicios.models import Product

class AmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'nombre']

class RoomSerializer(serializers.ModelSerializer):
    room_type_name = serializers.CharField(source='room_type.product.nombre', read_only=True)

    class Meta:
        model = Room
        fields = ['id', 'numero_habitacion', 'housekeeping_status', 'room_type', 'room_type_name']

class ProductForRoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['nombre', 'base_price']

class RoomTypeSerializer(serializers.ModelSerializer):
    product = ProductForRoomTypeSerializer()
    amenities = serializers.PrimaryKeyRelatedField(queryset=Amenity.objects.all(), many=True, required=False)

    class Meta:
        model = RoomType
        fields = ['id', 'product', 'capacidad', 'amenities']

    def create(self, validated_data):
        product_data = validated_data.pop('product')
        amenities = validated_data.pop('amenities', [])

        # El TenantManager se asegura de que esto sea seguro
        product = Product.objects.create(**product_data, nature=Product.ProductNature.SERVICE)

        room_type = RoomType.objects.create(product=product, **validated_data)
        if amenities:
            room_type.amenities.set(amenities)

        return room_type
