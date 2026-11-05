from django.db import models
from apps.core_erp.base_models import TenantAwareModel

class BankAccount(TenantAwareModel):
    name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

class BankTransaction(TenantAwareModel):
    """
    Hallazgo 17: Conciliación Bancaria.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('MATCHED', 'Conciliado'),
        ('UNMATCHED', 'No Coincide'),
        ('REVIEW_REQUIRED', 'Requiere Revisión'),
    ]

    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')
    external_id = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, default='COP')
    balance_after = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reconciled_with_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
