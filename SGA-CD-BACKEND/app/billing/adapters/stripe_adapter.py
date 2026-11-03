import stripe
from typing import Dict, Optional
from app.core.config import settings
from app.billing.base_adapter import BaseAdapter

class StripeAdapter(BaseAdapter):
    """
    Adapter for interacting with the Stripe payment gateway.
    """

    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    def create_payment_intent(
        self,
        *,
        amount: int,
        currency: str,
        user_id: int,
        payment_methods: Optional[Dict] = None
    ) -> Dict:
        """
        Creates a PaymentIntent with Stripe.
        Amount should be in the smallest currency unit (e.g., cents).
        Optionally accepts custom payment_methods configuration.
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency.lower(),
                automatic_payment_methods={"enabled": True}
                if payment_methods is None else payment_methods,
                metadata={"user_id": user_id}
            )
            return {"client_secret": intent.client_secret}
        except Exception as e:
            raise ValueError(f"Could not create payment intent with Stripe: {e}")

    def verify_webhook(self, *, payload: bytes, signature: str) -> stripe.Event:
        """
        Verifies an incoming webhook from Stripe.
        'payload' should be the raw request body as bytes.
        """
        try:
            event = stripe.Webhook.construct_event(
                payload=payload,
                sig_header=signature,
                secret=self.webhook_secret
            )
            return event
        except ValueError as e:
            # Invalid payload
            raise ValueError(f"Invalid webhook payload: {e}")
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            raise ValueError(f"Invalid webhook signature: {e}")