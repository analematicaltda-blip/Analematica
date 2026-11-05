from .models import HoldingRegion, TaxRule

class RegionalManager:
    """
    Gestiona la localización y cumplimiento normativo regional (Fase 6).
    """

    @staticmethod
    def get_regional_config(region_code):
        region = HoldingRegion.objects.filter(country_code=region_code).first()
        if not region:
            return None

        return {
            "country": region.name,
            "currency": region.default_currency.code,
            "language": region.language_code,
            "taxes": [
                {"name": t.name, "rate": float(t.percentage)}
                for t in region.tax_rules.filter(is_active=True)
            ]
        }

    @staticmethod
    def get_localized_pricing(base_price, region_code):
        """
        Ajusta el precio según la moneda regional.
        """
        region = HoldingRegion.objects.filter(country_code=region_code).first()
        if not region:
            return base_price

        # Conversión simple usando el rate de la moneda regional
        rate = region.default_currency.exchange_rate_to_base
        return base_price * rate
