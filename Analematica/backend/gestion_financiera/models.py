from django.db import models
from apps.core_erp.base_models import BaseBankAccount, BasePayment as BaseBankTransaction, BasePaymentOrder

class CuentaBancaria(BaseBankAccount):
    perfil_ref_id = models.UUIDField()

    class Meta:
        app_label = 'admin_financiera'
        verbose_name = "Cuenta Bancaria (Admin)"

class TransaccionBancaria(BaseBankTransaction):
    cuenta = models.ForeignKey(CuentaBancaria, on_delete=models.CASCADE, related_name='admin_transacciones')

    class Meta:
        app_label = 'admin_financiera'
        verbose_name = "Transacción Bancaria (Admin)"

class OrdenPago(BasePaymentOrder):
    class EstadoPago(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        PAGADA = 'PAGADA', 'Pagada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    perfil_ref_id = models.UUIDField()
    cuenta_bancaria_ref_id = models.UUIDField()

    class Meta:
        app_label = 'admin_financiera'
        verbose_name = "Orden de Pago (Admin)"
