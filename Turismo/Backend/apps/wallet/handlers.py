import logging
from apps.core_erp.event_bus import EventBus
from .services.wallet_service import WalletService
from api.models import CustomUser

logger = logging.getLogger(__name__)

class WalletEventHandlers:
    """
    Manejadores de eventos para el dominio de Wallet.
    Procesa transacciones solicitadas por otros dominios.
    """

    @staticmethod
    def handle_payment_request(payload: dict):
        """
        Procesa un pago solicitado externamente (Ej: desde Turismo o Comercial).
        """
        customer_id = payload.get('customer_id')
        target_user_id = payload.get('target_user_id')
        amount = payload.get('amount')
        description = payload.get('description', 'Pago automático')
        related_id = payload.get('related_service_id') or payload.get('reservation_id')

        customer = CustomUser.objects.filter(id=customer_id).first()
        target_user = CustomUser.objects.filter(id=target_user_id).first()

        if not customer or not target_user:
            logger.error(f"Wallet: No se pudo procesar pago. Usuario origen o destino no encontrado.")
            return

        wallet_service = WalletService(user=customer)
        try:
            tx = wallet_service.pay_to_user(
                target_user=target_user,
                amount=amount,
                related_service_id=related_id,
                description=description
            )
            logger.info(f"Wallet: Pago procesado exitosamente ID {tx.id}")
        except Exception as e:
            logger.error(f"Wallet: Error al procesar pago externo: {e}")

    @staticmethod
    def register_all():
        """
        Registra los suscriptores en el EventBus.
        """
        EventBus.subscribe('WALLET_PAYMENT_REQUESTED', WalletEventHandlers.handle_payment_request)
        logger.info("Wallet Event Handlers registrados.")
