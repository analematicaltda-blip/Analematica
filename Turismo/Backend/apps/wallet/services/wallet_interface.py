from abc import ABC, abstractmethod
from api.models import CustomUser

class WalletInterface(ABC):
    """
    Contrato de Interfaz para el Monedero Soberano (Fase 18).
    Define los métodos permitidos para consumo externo (ej. Delivery).
    """
    @abstractmethod
    def authorize_payment(self, to_wallet_id, amount, related_service_id=None, description=""):
        """
        Solicita una autorización/retención de fondos para un pago futuro.
        """
        pass

    @abstractmethod
    def release_payment(self, transaction_id):
        """
        Libera y confirma un pago previamente autorizado.
        """
        pass

    @abstractmethod
    def cancel_authorization(self, transaction_id):
        """
        Cancela una autorización y libera los fondos retenidos.
        """
        pass

    @abstractmethod
    def pay(self, to_wallet_id, amount, related_service_id=None, description="", intention_id=None):
        """
        Ejecuta un pago directo.
        """
        pass

    @abstractmethod
    def pay_to_user(self, target_user, amount, related_service_id=None, description=""):
        """
        Ejecuta un pago directo a un usuario, resolviendo su monedero internamente.
        """
        pass

    @abstractmethod
    def get_wallet_balance(self, owner_id=None, owner_type=None):
        """
        Consulta el saldo disponible de un monedero por propietario.
        """
        pass
