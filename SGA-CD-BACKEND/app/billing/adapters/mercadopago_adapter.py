import mercadopago
import uuid
from typing import Dict
from app.core.config import settings
from app.billing.base_adapter import BaseAdapter

class MercadoPagoAdapter(BaseAdapter):
    def __init__(self):
        self.sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

    def create_payment_intent(self, *, amount: int, currency: str, user_id: int, payment_methods: Dict = None) -> Dict:
        try:
            preference_data = {
                "items": [
                    {
                        "title": "Suscripción SGA-CD",
                        "quantity": 1,
                        "unit_price": float(amount / 100)
                    }
                ],
                "back_urls": {
                    "success": "http://localhost:3000/payment_success.html",
                    "failure": "http://localhost:3000/payment_cancel.html",
                },
                "auto_return": "approved",
                "external_reference": f"user_{user_id}_suscripcion_{uuid.uuid4()}"
            }
            if payment_methods:
                preference_data["payment_methods"] = payment_methods

            preference_response = self.sdk.preference().create(preference_data)
            preference = preference_response["response"]
            return {"redirect_url": preference["init_point"]}
        except Exception as e:
            raise ValueError(f"Could not create payment preference with Mercado Pago: {e}")

    def verify_webhook(self, *, payload: dict, signature: str = None) -> any:
        print(f"Received Mercado Pago Webhook: {payload}")
        return {"status": "received", "payload": payload}
