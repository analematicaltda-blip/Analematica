from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseAdapter(ABC):
    """
    Abstract Base Class for all payment gateway adapters.
    Defines the common interface for creating payments and handling webhooks.
    """

    @abstractmethod
    def create_payment_intent(
        self,
        *,
        amount: int,
        currency: str,
        user_id: int,
        payment_methods: Optional[Dict] = None
    ) -> Dict:
        """
        Creates a payment intent (or equivalent) with the gateway.

        Args:
            amount (int): Amount in the smallest currency unit (e.g., cents).
            currency (str): Currency code (e.g., "usd", "cop").
            user_id (int): ID of the user making the payment.
            payment_methods (Optional[Dict]): Extra configuration for accepted/excluded payment methods.

        Returns:
            Dict: Details required by the frontend to complete the payment (e.g., client_secret for Stripe).
        """
        pass

    @abstractmethod
    def verify_webhook(self, *, payload: Any, signature: str) -> Any:
        """
        Verifies the authenticity of an incoming webhook.

        Args:
            payload (Any): Raw request body (bytes or dict depending on gateway).
            signature (str): Signature header provided by the gateway.

        Returns:
            Any: Parsed event object if successful.

        Raises:
            ValueError: If the payload is invalid or the signature is not valid.
        """
        pass