import hashlib
import uuid
from typing import Dict
from app.core.config import settings
from app.billing.base_adapter import BaseAdapter

class WompiAdapter(BaseAdapter):
    def __init__(self):
        self.public_key = settings.WOMPI_PUBLIC_KEY
        self.secret_key = settings.WOMPI_SECRET_KEY
        self.endpoint = "https://sandbox.wompi.co/v1/transactions"

    def create_payment_intent(self, *, amount: int, currency: str, user_id: int, payment_methods: Dict = None) -> Dict:
        reference = f"sga_user_{user_id}_{uuid.uuid4()}"
        integrity_signature = f"{reference}{amount}{currency.upper()}{self.secret_key}"
        signature = hashlib.sha256(integrity_signature.encode("utf-8")).hexdigest()

        return {"redirect_url": f"https://checkout.wompi.co/p/?public-key={self.public_key}&currency={currency.upper()}&amount-in-cents={amount}&reference={reference}&signature:integrity={signature}"}

    def verify_webhook(self, *, payload: dict, signature: str = None) -> any:
        print(f"Received Wompi Webhook: {payload}")
        return {"status": "verified", "payload": payload}
