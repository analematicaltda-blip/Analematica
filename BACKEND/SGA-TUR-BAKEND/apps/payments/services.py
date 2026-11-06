
from decimal import Decimal
from apps.orders.services import OrderService
from .models import Payment
from apps.cart.models import Cart
from apps.comercial.models import Subscription
from datetime import timedelta

class PaymentService:
    @staticmethod
    def initiate_payment(cart: Cart, provider: str) -> Payment:
        order = OrderService.create_order_from_cart(cart)
        payment = Payment.objects.create(
            order=order,
            user=cart.user,
            amount=order.total_amount,
            provider=provider,
            status='INIT'
        )
        return payment

    @staticmethod
    def confirm_payment(transaction_id: str):
        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            if payment.status == 'PAID':
                return

            payment.status = 'PAID'
            payment.save()

            # Crear suscripción
            order = payment.order
            for item in order.items.all():
                # Asumimos que la frecuencia determina la duración
                duration_days = 365 if item.plan.frecuencia == 'ANUAL' else 182 if item.plan.frecuencia == 'SEMESTRAL' else 30
                end_date = timedelta(days=duration_days * item.quantity)

                # Buscamos el perfil del prestador asociado al usuario
                # NOTA: Esto asume que el user tiene un perfil de prestador.
                # Se necesita una lógica más robusta para diferentes tipos de usuarios.
                client_profile = getattr(order.user, 'perfil_prestador', None)
                if client_profile:
                    Suscripcion.objects.create(
                        cliente=client_profile,
                        plan=item.plan,
                        fecha_inicio=payment.updated_at.date(),
                        fecha_fin=payment.updated_at.date() + end_date,
                        is_active=True
                    )

            # Vaciar carro
            cart = Cart.objects.get(user=order.user)
            cart.items.all().delete()

        except Payment.DoesNotExist:
            raise ValueError(f"No se encontró un pago con transaction_id {transaction_id}")

    @staticmethod
    def get_payment_status(payment_id: int):
        try:
            payment = Payment.objects.get(id=payment_id)
            return payment.status
        except Payment.DoesNotExist:
            return None
