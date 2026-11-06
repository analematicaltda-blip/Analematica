import uuid
from django.db import models
from .bank_account_model import BankAccount

class BankTransaction(models.Model):
    class Direction(models.TextChoices):
        IN = 'IN', 'Incoming'
        OUT = 'OUT', 'Outgoing'

    class ReconciliationStatus(models.TextChoices):
        UNMATCHED = 'UNMATCHED', 'Unmatched'
        MATCHED = 'MATCHED', 'Matched'
        PARTIAL = 'PARTIAL', 'Partial Match'
        OVERPAID = 'OVERPAID', 'Overpaid'
        UNDERPAID = 'UNDERPAID', 'Underpaid'
        IGNORED = 'IGNORED', 'Ignored'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='transactions')

    external_id = models.CharField(max_length=100, unique=True, db_index=True) # Idempotency

    transaction_date = models.DateField()
    value_date = models.DateField()

    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3)
    direction = models.CharField(max_length=3, choices=Direction.choices)

    reference = models.CharField(max_length=100, blank=True, db_index=True)

    # Reconciliation data
    matched = models.BooleanField(default=False)
    reconciliation_status = models.CharField(
        max_length=20,
        choices=ReconciliationStatus.choices,
        default=ReconciliationStatus.UNMATCHED
    )
    matched_invoice_id = models.UUIDField(null=True, blank=True)

    # Audit
    audit_hash = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_date} - {self.amount} {self.currency} ({self.direction})"

    class Meta:
        verbose_name = "Transacción Bancaria SaaS"
        verbose_name_plural = "Transacciones Bancarias SaaS"
        app_label = 'treasury_automation'
        ordering = ['-transaction_date']
