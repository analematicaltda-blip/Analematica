from django.db import models
from django.conf import settings
from apps.core_erp.base_models import (
    BaseErpModel, TenantAwareModel, LedgerAccount as BaseAccount,
    BaseJournalEntry, BaseJournalLine as BaseJournalLineBase,
    FinancialPeriod as BaseFinancialPeriod
)

class AccountingTenantModel(TenantAwareModel):
    class Meta:
        abstract = True

class ChartOfAccounts(AccountingTenantModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.tenant})"

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Chart of Accounts"

class Account(BaseAccount, AccountingTenantModel):
    # BaseAccount has code, name, type, parent_account
    chart_of_accounts = models.ForeignKey(ChartOfAccounts, on_delete=models.CASCADE, related_name='accounts')
    initial_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    # Phase B: IFRS and Consolidation mapping
    ifrs_mapping = models.CharField(max_length=50, null=True, blank=True)
    consolidation_code = models.CharField(max_length=50, null=True, blank=True)
    is_consolidation_account = models.BooleanField(default=False)

    class Meta:
        app_label = 'core_erp'
        unique_together = ('chart_of_accounts', 'code')

    def __str__(self):
        return f"{self.code} - {self.name}"

class FiscalPeriod(BaseFinancialPeriod, AccountingTenantModel):
    class Meta:
        app_label = 'core_erp'
        verbose_name = "Fiscal Period"

class JournalEntry(BaseJournalEntry, AccountingTenantModel):
    # BaseJournalEntry has date, reference, description, is_posted
    period = models.ForeignKey(FiscalPeriod, on_delete=models.PROTECT, related_name='entries')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    event_type = models.CharField(max_length=100) # Mandatory in Phase 3
    is_reversal = models.BooleanField(default=False)
    reversed_entry_id = models.UUIDField(null=True, blank=True)
    correlation_id = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    rule_version = models.CharField(max_length=10, default="1.0")
    financial_event_id = models.CharField(max_length=255, db_index=True, null=True, blank=True)

    # Phase 3: Irreversible Posting & Chained Hash
    base_currency = models.CharField(max_length=3, default='COP')
    posted_at = models.DateTimeField(null=True, blank=True)
    system_hash = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    previous_hash = models.CharField(max_length=64, null=True, blank=True)
    immutable_signature = models.TextField(null=True, blank=True)

    def compute_hash(self):
        """
        Calcula el hash SHA-256 del asiento incluyendo sus líneas para garantizar integridad.
        """
        import hashlib
        import json
        from decimal import Decimal

        def default_serializer(obj):
            if isinstance(obj, Decimal):
                return str(obj)
            return obj

        # Recopilar datos base del asiento
        header_data = {
            "id": str(self.id),
            "date": str(self.date),
            "tenant": str(self.tenant_id),
            "event_type": self.event_type,
            "previous_hash": self.previous_hash or "",
        }

        # Recopilar datos de las líneas (deben existir para el hash final)
        lines_data = []
        for line in self.lines.all().order_by('id'):
            lines_data.append({
                "account": str(line.account_id),
                "debit": line.debit_amount,
                "credit": line.credit_amount
            })

        full_content = {
            "header": header_data,
            "lines": lines_data
        }

        content_str = json.dumps(full_content, sort_keys=True, default=default_serializer)
        return hashlib.sha256(content_str.encode()).hexdigest()

    def save(self, *args, **kwargs):
        if self.pk and JournalEntry.plain_objects.get(pk=self.pk).is_posted:
            # Phase 3.5: Irreversibility - No editing posted entries
            raise PermissionError("Posted journal entries cannot be modified. Use reversal instead.")

        # Lógica de encadenamiento al postear
        if self.is_posted and not self.system_hash:
            from django.utils import timezone
            # 1. Obtener el hash del asiento anterior (por fecha de posteo)
            last_entry = JournalEntry.plain_objects.filter(
                is_posted=True,
                tenant=self.tenant
            ).order_by('-posted_at', '-id').first()

            if last_entry:
                self.previous_hash = last_entry.system_hash
            else:
                self.previous_hash = "GENESIS_BLOCK_SARITA_V1"

            # 2. Registrar timestamp de posteo
            if not self.posted_at:
                self.posted_at = timezone.now()

            # 3. El hash final se calcula después de asegurar que las líneas existen.
            # Nota: Esto requiere que el AccountingEngine llame a un método .post()
            # que ejecute esta lógica después de verificar el balance.
            self.system_hash = self.compute_hash()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Phase 3.5: Irreversibility - No physical deletion
        raise PermissionError("Journal entries cannot be physically deleted. Use reversal to invalidate.")

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Journal Entry"
        ordering = ['posted_at', 'id']

class AccountingAuditLog(AccountingTenantModel):
    """
    Tabla de auditoría obligatoria para acciones contables (Fase 3.11).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    action = models.CharField(max_length=100) # Ej: POST, REVERSE
    reference_entry = models.ForeignKey(JournalEntry, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    integrity_hash = models.CharField(max_length=64) # SHA256(Entry + User + Action)

    class Meta:
        app_label = 'core_erp'

class LedgerEntry(TenantAwareModel):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='ledger_entries')
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    # Phase B: Transaction vs Base Amounts
    currency = models.CharField(max_length=3, default='COP')
    amount_transaction = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    amount_base = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    description = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.journal_entry.is_posted:
            raise PermissionError("Lines of posted journal entries cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.journal_entry.is_posted:
            raise PermissionError("Lines of posted journal entries cannot be deleted.")
        super().delete(*args, **kwargs)

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Ledger Entry"
