import logging
from decimal import Decimal
from django.utils import timezone
from .models import Currency, FXRateTable

logger = logging.getLogger(__name__)

class FXEngine:
    """
    Motor de Conversión de Divisas SARITA.
    Proporciona tasas de cambio versionadas y conversiones determinísticas.
    """

    @staticmethod
    def get_rate(base_code: str, target_code: str, version: int = None):
        """
        Obtiene la tasa de cambio más reciente o una versión específica.
        """
        query = {
            "base_currency__code": base_code,
            "target_currency__code": target_code,
        }
        if version:
            query["version"] = version

        rate_obj = FXRateTable.objects.filter(**query).order_by('-effective_from', '-version').first()

        if not rate_obj:
            if base_code == target_code:
                return Decimal('1.0')
            raise ValueError(f"No se encontró tasa de cambio para {base_code} -> {target_code}")

        return rate_obj.rate

    @staticmethod
    def convert(amount: Decimal, from_currency: str, to_currency: str, version: int = None) -> Decimal:
        """
        Convierte un monto entre dos divisas.
        """
        if from_currency == to_currency:
            return amount

        rate = FXEngine.get_rate(from_currency, to_currency, version)
        return (amount * rate).quantize(Decimal('1.00'))

    @staticmethod
    def update_rate(base_code: str, target_code: str, rate: Decimal, user_id=None):
        """
        Actualiza o crea una nueva versión de la tasa de cambio.
        """
        base = Currency.objects.get(code=base_code)
        target = Currency.objects.get(code=target_code)

        last_version = FXRateTable.objects.filter(
            base_currency=base,
            target_currency=target
        ).order_by('-version').first()

        new_version = (last_version.version + 1) if last_version else 1

        new_rate = FXRateTable.objects.create(
            base_currency=base,
            target_currency=target,
            rate=rate,
            effective_from=timezone.now(),
            version=new_version
        )

        logger.info(f"FX Engine: Nueva tasa registrada {base_code}/{target_code}: {rate} (v{new_version})")
        return new_rate
