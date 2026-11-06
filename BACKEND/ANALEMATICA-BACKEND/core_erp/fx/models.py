from django.db import models
from apps.core_erp.base_models import BaseErpModel

class Currency(BaseErpModel):
    code = models.CharField(max_length=3, unique=True) # ISO 4217
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class FXRateTable(BaseErpModel):
    base_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='base_rates')
    target_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='target_rates')
    rate = models.DecimalField(max_digits=18, decimal_places=6)
    effective_from = models.DateTimeField()
    version = models.IntegerField(default=1)
    is_official = models.BooleanField(default=True)

    class Meta:
        unique_together = ('base_currency', 'target_currency', 'version')
        ordering = ['-effective_from']

    def __str__(self):
        return f"1 {self.base_currency.code} = {self.rate} {self.target_currency.code} (v{self.version})"
