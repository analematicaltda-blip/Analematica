
from rest_framework import serializers
from .models import Cart, CartItem
from apps.admin_plataforma.serializers import PlanSerializer

class CartItemSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'plan', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_key', 'items', 'total_cart_price', 'updated_at']

    def get_total_cart_price(self, cart):
        return sum(item.total_price for item in cart.items.all())
