
from django.conf import settings
from .models import Cart, CartItem
from apps.comercial.models import Plan

class CartService:
    """
    Servicio para manejar la lógica de negocio del carro de compras.
    """

    @staticmethod
    def get_or_create_cart(user):
        """Obtiene o crea un carro para un usuario dado."""
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_item_to_cart(user, plan_id: int, quantity: int = 1):
        """Añade un ítem al carro del usuario."""
        cart = CartService.get_or_create_cart(user)

        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
        except Plan.DoesNotExist:
            raise ValueError("El plan no existe o no está activo")

        cart_item, created = CartItem.objects.get_or_create(cart=cart, plan=plan)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
        return cart

    @staticmethod
    def remove_item_from_cart(user, item_id: int):
        """Elimina un ítem del carro del usuario."""
        cart = CartService.get_or_create_cart(user)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
            item.delete()
        except CartItem.DoesNotExist:
            raise ValueError("El ítem no existe en el carro")

        return cart
