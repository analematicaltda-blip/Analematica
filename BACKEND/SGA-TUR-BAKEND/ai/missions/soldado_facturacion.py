import logging
from apps.usage_billing.billing_engine import BillingEngine

logger = logging.getLogger(__name__)

class BillingSoldier:
    """NIVEL 6 - SOLDADO DE FACTURACIÓN"""
    async def execute(self, mission_data):
        data = mission_data.get("data", {})
        logger.info(f"Soldado Facturación: Generando factura para venta {data.get('venta_id')}")

        try:
            # Orquestación de servicio real ( BillingEngine )
            invoice = await BillingEngine.create_invoice(data)
            return {
                "status": "success",
                "invoice_number": invoice.invoice_number,
                "amount": float(invoice.total_amount)
            }
        except Exception as e:
            logger.error(f"Error en facturación: {e}")
            return {"status": "error", "message": str(e)}
