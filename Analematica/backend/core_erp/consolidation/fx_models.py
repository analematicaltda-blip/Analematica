from django.db import models
from apps.core_erp.base_models import BaseErpModel

class FXRateTable(BaseErpModel):
    """
    Standardized FX rates for Holding consolidation.
    Versioned and event-driven updates.
    """
    from_currency = models.CharField(max_length=3)
    to_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=6)

    version = models.IntegerField(default=1)
    effective_date = models.DateField()

    is_active = models.BooleanField(default=True)

    __schema_version__ = "v2.1"

    class Meta:
        app_label = 'core_erp'
        unique_together = ('from_currency', 'to_currency', 'version')
        verbose_name = "FX Rate"
        verbose_name_plural = "FX Rates"

    def __str__(self):
        return f"{self.from_currency}/{self.to_currency}: {self.rate} (v{self.version})"
