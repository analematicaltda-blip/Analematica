from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class CorporateBudget(TenantAwareModel):
    """
    High-level corporate budget for EOS.
    """
    legal_entity_id = models.UUIDField(null=True, blank=True)
    fiscal_year = models.IntegerField()

    revenue_target = models.DecimalField(max_digits=20, decimal_places=2)
    expense_limit = models.DecimalField(max_digits=20, decimal_places=2)
    ebitda_target = models.DecimalField(max_digits=20, decimal_places=2)

    actual_revenue = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    actual_expense = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    status = models.CharField(max_length=20, choices=[('DRAFT','Draft'), ('APPROVED','Approved'), ('LOCKED','Locked')], default='DRAFT')

    class Meta:
        app_label = 'enterprise'
        verbose_name = "Corporate Budget"
        unique_together = ('tenant', 'legal_entity_id', 'fiscal_year')
