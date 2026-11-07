
from django.db import transaction
from apps.cart.models import Cart
from .models import Order, OrderItem

class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order_from_cart(cart: Cart) -> Order:
        """
        Crea una Order y sus OrderItems a partir de un Cart.
        Esta es una operación atómica.
        """
        if cart.items.count() == 0:
            raise ValueError("No se puede crear una orden de un carro vacío.")

        total_amount = sum(item.total_price for item in cart.items.all())

        order = Order.objects.create(
            user=cart.user,
            total_amount=total_amount
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                plan=cart_item.plan,
                quantity=cart_item.quantity,
                price_at_purchase=cart_item.plan.precio
            )

        return order
