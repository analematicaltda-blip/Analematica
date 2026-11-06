from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.billing.base_adapter import BaseAdapter
from app.billing.adapters.stripe_adapter import StripeAdapter
from app.billing.adapters.mercadopago_adapter import MercadoPagoAdapter
from app.billing.adapters.wompi_adapter import WompiAdapter
from app.crud import billing as crud_billing
from app.schemas.billing import PaymentCreate, SubscriptionUpdate


class BillingService:
    def __init__(self, db: Session):
        self.db = db
        self.adapters = {
            "stripe": StripeAdapter(),
            "mercadopago": MercadoPagoAdapter(),
            "wompi": WompiAdapter(),
        }

    def get_adapter(self, gateway_name: str) -> BaseAdapter:
        """
        Retrieve the payment adapter for a given gateway.
        """
        adapter = self.adapters.get(gateway_name)
        if not adapter:
            raise ValueError(f"No adapter found for gateway: {gateway_name}")
        return adapter

    def create_payment_intent(
        self,
        *,
        gateway_name: str,
        amount: float,
        currency: str,
        user_id: int,
        payment_methods: dict = None,
    ):
        """
        Creates a payment intent using the specified gateway.
        Also creates a pending Payment record in the database linked to the user's subscription.
        """
        adapter = self.get_adapter(gateway_name)

        # Validate subscription
        subscription = crud_billing.get_subscription_by_tenant(
            self.db, inquilino_id=user_id
        )
        if not subscription:
            raise ValueError("No subscription found for user.")

        # Create a pending payment record in DB
        payment_in = PaymentCreate(
            subscription_id=subscription.id,
            inquilino_id=user_id,
            amount=amount,
            currency=currency,
            status="pending",
            gateway_name=gateway_name,
        )
        db_payment = crud_billing.create_payment(self.db, obj_in=payment_in)

        # Create payment intent with the gateway
        intent_details = adapter.create_payment_intent(
            amount=int(amount * 100),  # always send cents
            currency=currency,
            user_id=user_id,
            payment_methods=payment_methods,
        )

        # Optionally, update db_payment with gateway intent ID if returned
        return intent_details

    def handle_webhook(self, *, gateway_name: str, payload: dict, signature: str):
        """
        Handles an incoming webhook from a payment gateway.
        Verifies authenticity and updates payment/subscription status accordingly.
        """
        adapter = self.get_adapter(gateway_name)
        event = adapter.verify_webhook(payload=payload, signature=signature)

        if gateway_name == "stripe" and event.type == "payment_intent.succeeded":
            payment_intent = event.data.object
            transaction_id = payment_intent.id
            db_payment = crud_billing.get_payment_by_gateway_transaction_id(
                self.db, transaction_id=transaction_id
            )

            if db_payment:
                if db_payment.status == "succeeded":
                    # Idempotency check: Already processed, do not extend twice
                    return {"status": "success", "message": "Evento ya procesado (idempotente)"}

                if db_payment.status == "pending":
                    crud_billing.update_payment_status(
                        self.db, db_obj=db_payment, status="succeeded"
                    )

                    # Extend subscription
                    subscription = db_payment.subscription
                    new_end_date = (subscription.end_date or datetime.utcnow()) + timedelta(
                        days=30
                    )
                    sub_update = SubscriptionUpdate(end_date=new_end_date, status="active")
                    crud_billing.update_subscription(
                        self.db, db_obj=subscription, obj_in=sub_update
                    )
                    print(f"Subscription for user {subscription.inquilino_id} extended.")

        # TODO: Implement webhook handling for MercadoPago and Wompi
        print(f"Webhook event processed for {gateway_name}: {event.type}")

        return {"status": "success"}