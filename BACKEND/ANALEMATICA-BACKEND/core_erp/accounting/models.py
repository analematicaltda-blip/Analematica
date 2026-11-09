from django.db import models, transaction
from django.conf import settings
from decimal import Decimal
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
    initial_balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
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
    hash_version = models.CharField(max_length=16, default="legacy")

    def compute_hash(self):
        """
        Calcula el hash SHA-256 del asiento incluyendo sus líneas para garantizar integridad.
        """
        if self.hash_version == 'v2':
            from .integrity import journal_hash
            return journal_hash(self, list(LedgerEntry.plain_objects.filter(journal_entry_id=self.pk).select_related('account')), self.previous_hash)
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
        for line in LedgerEntry.plain_objects.filter(journal_entry_id=self.pk).order_by('id'):
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

    @transaction.atomic
    def save(self, *args, **kwargs):
        from .validation import lock_company
        from .exceptions import TenantMismatchError
        lock_company(self.tenant_id)
        stored = JournalEntry.plain_objects.select_for_update().filter(pk=self.pk).first()
        if stored and str(stored.tenant_id) != str(self.tenant_id):
            raise TenantMismatchError('A journal cannot move between accounting companies.')
        if stored and stored.is_posted:
            raise PermissionError('Posted journal entries cannot be modified. Use reversal instead.')
        if self.is_posted and not getattr(self, '_validated_post', False):
            raise PermissionError('Use LedgerEngine to post a journal entry.')
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
    debit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    credit_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))

    # Phase B: Transaction vs Base Amounts
    currency = models.CharField(max_length=3, default='COP')
    amount_transaction = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    amount_base = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))

    description = models.CharField(max_length=255, blank=True, null=True)

    def _locked_parent(self):
        from .validation import lock_company
        from .exceptions import TenantMismatchError
        lock_company(self.tenant_id)
        stored = LedgerEntry.plain_objects.filter(pk=self.pk).first()
        if stored and stored.journal_entry_id != self.journal_entry_id:
            raise PermissionError('Journal lines cannot be reassigned.')
        parent = JournalEntry.plain_objects.select_for_update().get(pk=self.journal_entry_id,tenant_id=self.tenant_id)
        if str(parent.tenant_id) != str(self.tenant_id):
            raise TenantMismatchError('Journal and line company mismatch.')
        if parent.is_posted:
            raise PermissionError('Lines of posted journal entries cannot be modified.')
        return parent

    @transaction.atomic
    def save(self, *args, **kwargs):
        from .validation import money
        from .exceptions import TenantMismatchError, UnbalancedEntryError
        self._locked_parent()
        if not Account.plain_objects.filter(pk=self.account_id,tenant_id=self.tenant_id,chart_of_accounts__tenant_id=self.tenant_id).exists():
            raise TenantMismatchError('Account does not belong to this accounting company.')
        self.debit_amount=money(self.debit_amount);self.credit_amount=money(self.credit_amount)
        if (self.debit_amount>0)==(self.credit_amount>0):
            raise UnbalancedEntryError('A line requires exactly one positive side.')
        self.amount_transaction=money(self.amount_transaction);self.amount_base=money(self.amount_base)
        super().save(*args, **kwargs)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        self._locked_parent()
        super().delete(*args, **kwargs)

    class Meta:
        app_label = 'core_erp'
        verbose_name = "Ledger Entry"


class AccountingEventReceipt(BaseErpModel):
    tenant = models.ForeignKey('core_erp.Tenant', on_delete=models.PROTECT)
    event_id = models.CharField(max_length=255)
    payload_hash = models.CharField(max_length=64)
    journal = models.ForeignKey(JournalEntry, on_delete=models.PROTECT)

    class Meta:
        app_label = 'core_erp'
        constraints = [models.UniqueConstraint(fields=['tenant','event_id'],name='accounting_event_once_per_tenant')]
