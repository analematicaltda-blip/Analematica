import uuid
from django.db import models

class BankAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_id = models.UUIDField(db_index=True) # Multi-empresa

    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50, help_text="Masked account number.")

    currency = models.CharField(max_length=3, default='COP')
    iban = models.CharField(max_length=34, blank=True, null=True)
    swift = models.CharField(max_length=11, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number} ({self.currency})"

    class Meta:
        verbose_name = "Cuenta Bancaria SaaS"
        verbose_name_plural = "Cuentas Bancarias SaaS"
        app_label = 'treasury_automation'
