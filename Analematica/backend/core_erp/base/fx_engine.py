from decimal import Decimal
from django.db import models
from django.utils import timezone
from apps.core_erp.base_models import BaseErpModel

class FXRate(BaseErpModel):
    """
    Motor FX: Historial de tasas de cambio.
    """
    source = models.CharField(max_length=50, default='INTERNAL')
    timestamp = models.DateTimeField(default=timezone.now)
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=6)

    class Meta:
        app_label = 'core_erp'
        unique_together = ('base_currency', 'target_currency', 'timestamp')

class FXEngine:
    """
    Servicio de cambio de moneda y revaluación.
    """

    @staticmethod
    def get_latest_rate(from_currency: str, to_currency: str) -> Decimal:
        if from_currency == to_currency:
            return Decimal('1.0')

        rate_obj = FXRate.objects.filter(
            base_currency=from_currency,
            target_currency=to_currency
        ).order_by('-timestamp').first()

        if rate_obj:
            return rate_obj.rate

        # Fallback for testing/dev
        fallbacks = {
            ('USD', 'COP'): Decimal('4000.0'),
            ('COP', 'USD'): Decimal('0.00025'),
        }
        return fallbacks.get((from_currency, to_currency), Decimal('1.0'))

    @staticmethod
    def convert(amount: Decimal, from_curr: str, to_curr: str) -> Decimal:
        rate = FXEngine.get_latest_rate(from_curr, to_curr)
        return (amount * rate).quantize(Decimal('0.01'))

    @staticmethod
    def revaluate_account(account_id: str, target_currency: str):
        """
        Revaluación automática de cuentas monetarias (Fase 7 - II.6.2).
        Detecta diferencia cambiaria y propone ajuste.
        """
        # 1. Obtener balance en moneda original
        # 2. Calcular balance teórico en target_currency a tasa de cierre
        # 3. Calcular diferencia (Realized/Unrealized Gain or Loss)
        pass
