import uuid
from django.db import models

class HoldingCurrency(models.Model):
    """Monedas soportadas por el holding global."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=3, unique=True, help_text="Ej: USD, EUR, COP")
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=5)
    exchange_rate_to_base = models.DecimalField(max_digits=18, decimal_places=6, default=1.0)
    is_base_currency = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.code} - {self.name}"

class HoldingRegion(models.Model):
    """Regiones geográficas / Países de operación."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    country_code = models.CharField(max_length=2, help_text="Ej: US, ES, CO")
    default_currency = models.ForeignKey(HoldingCurrency, on_delete=models.PROTECT)
    language_code = models.CharField(max_length=5, default="es-co")

    def __str__(self):
        return self.name

class HoldingEntity(models.Model):
    """Empresas o productos SaaS bajo el control del holding."""
    class VerticalType(models.TextChoices):
        TOURISM = 'TOURISM', 'Turismo'
        FINTECH = 'FINTECH', 'Finanzas'
        LOGISTICS = 'LOGISTICS', 'Logística'
        GOVERNMENT = 'GOVERNMENT', 'Gubernamental'
        GENERIC_SAAS = 'GENERIC_SAAS', 'SaaS Genérico'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, unique=True)
    vertical = models.CharField(max_length=50, choices=VerticalType.choices)
    region = models.ForeignKey(HoldingRegion, on_delete=models.PROTECT)
    base_currency = models.ForeignKey(HoldingCurrency, on_delete=models.PROTECT)

    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Empresa del Holding"
        verbose_name_plural = "Empresas del Holding"

class TaxRule(models.Model):
    """Reglas fiscales granulares por región."""
    region = models.ForeignKey(HoldingRegion, on_delete=models.CASCADE, related_name='tax_rules')
    name = models.CharField(max_length=100)
    tax_type = models.CharField(max_length=50, help_text="Ej: VAT, SalesTax, Retención")
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.percentage}%) - {self.region.name}"
