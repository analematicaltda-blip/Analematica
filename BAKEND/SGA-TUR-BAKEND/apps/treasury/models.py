import uuid
from django.db import models

class BankStatement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    statement_date = models.DateField()

    total_deposits = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    is_reconciled = models.BooleanField(default=False)

    class Meta:
        app_label = 'treasury'

class BankTransaction(models.Model):
    statement = models.ForeignKey(BankStatement, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)

    is_matched = models.BooleanField(default=False)
    matched_invoice_id = models.UUIDField(null=True, blank=True)

    class Meta:
        app_label = 'treasury'
