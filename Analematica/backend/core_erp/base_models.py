from django.db import models
import uuid
from django.utils import timezone
from apps.core_erp.tenancy.utils import get_current_tenant_id

class TenantQuerySet(models.QuerySet):
    def for_tenant(self, tenant_id=None):
        if tenant_id is None:
            tenant_id = get_current_tenant_id()
        if tenant_id:
            return self.filter(tenant_id=tenant_id)
        return self.none() # Absolute isolation: no tenant = no data

class TenantManager(models.Manager):
    def get_queryset(self):
        tenant_id = get_current_tenant_id()
        queryset = TenantQuerySet(self.model, using=self._db)
        if tenant_id:
            return queryset.filter(tenant_id=tenant_id)

        # Absolute isolation: If no tenant context is active, return empty.
        # This prevents accidental data leakage in global contexts.
        return queryset.none()

class BaseErpModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True

class TenantAwareModel(BaseErpModel):
    """
    Standardizes tenant isolation across all domain models.
    """
    tenant = models.ForeignKey(
        'core_erp.Tenant',
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_records",
        null=True,  # Initially nullable for migration safety
        blank=True
    )

    objects = TenantManager()
    plain_objects = models.Manager() # Escape hatch for administrative tasks

    def save(self, *args, **kwargs):
        # Auto-populate tenant from context if not set
        if not self.tenant_id:
            context_tenant_id = get_current_tenant_id()
            if context_tenant_id:
                self.tenant_id = context_tenant_id
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class CompanyBase(TenantAwareModel):
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    tax_id = models.CharField(max_length=50, null=True, blank=True)
    fiscal_regime = models.CharField(max_length=100, null=True, blank=True)
    currency = models.CharField(max_length=3, default='COP')
    country = models.CharField(max_length=100, default='Colombia')

    class Meta:
        abstract = True

class FinancialPeriod(TenantAwareModel):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('locked', 'Locked'),
    ]
    period_start = models.DateField(null=True)
    period_end = models.DateField(null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    class Meta:
        abstract = True

class LedgerAccount(TenantAwareModel):
    ACCOUNT_TYPES = [
        ('ASSET', 'Activo'),                # Clase 1
        ('LIABILITY', 'Pasivo'),           # Clase 2
        ('EQUITY', 'Patrimonio'),          # Clase 3
        ('REVENUE', 'Ingresos'),           # Clase 4
        ('EXPENSE', 'Gastos'),             # Clase 5
        ('COST_OF_SALES', 'Costos de Ventas'), # Clase 6
        ('PRODUCTION_COST', 'Costos de Producción o de Operación'), # Clase 7
        ('DEBTOR_ORDER', 'Cuentas de Orden Deudoras'), # Clase 8
        ('CREDITOR_ORDER', 'Cuentas de Orden Acreedoras'), # Clase 9
    ]
    code = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, null=True)
    parent_account = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_accounts')

    # Blueprint Alignment: Global + Local Mapping
    ifrs_code = models.CharField(max_length=50, null=True, blank=True)
    local_gaap_code = models.CharField(max_length=50, null=True, blank=True)
    consolidation_mapping = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True

class BaseJournalEntry(TenantAwareModel):
    date = models.DateField(default=timezone.now)
    reference = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_posted = models.BooleanField(default=False)
    currency = models.CharField(max_length=3, default='COP')
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=6, default=1.0)

    class Meta:
        abstract = True

class BaseJournalLine(BaseErpModel):  # Child of Entry, usually inherits context
    account_code = models.CharField(max_length=20, null=True, blank=True)
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True

class BaseInvoice(TenantAwareModel):
    number = models.CharField(max_length=50, null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=30, default='DRAFT')
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='COP')

    class Meta:
        abstract = True

class BaseInvoiceLine(BaseErpModel):
    description = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, default=1.00)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    class Meta:
        abstract = True

class BaseBankAccount(TenantAwareModel):
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    account_type = models.CharField(max_length=50, null=True, blank=True)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class BasePayment(TenantAwareModel):
    payment_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    method = models.CharField(max_length=50, null=True, blank=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    bank_fees = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)

    class Meta:
        abstract = True

class BasePaymentOrder(TenantAwareModel):
    payment_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    concept = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, default='PENDING')

    class Meta:
        abstract = True

class BaseWarehouse(TenantAwareModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True

class BaseInventoryMovement(TenantAwareModel):
    movement_type = models.CharField(max_length=50, null=True, blank=True)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    date = models.DateTimeField(auto_now_add=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

class BaseAuditTrail(TenantAwareModel):
    action = models.CharField(max_length=100, null=True, blank=True)
    entity_type = models.CharField(max_length=50, null=True, blank=True)
    entity_id = models.UUIDField(null=True)
    payload = models.JSONField(null=True) # Full state snapshot

    # Blueprint Alignment: Inmutable Audit with Delta
    previous_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)

    user_id = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    previous_hash = models.CharField(max_length=64, null=True, blank=True)
    integrity_hash = models.CharField(max_length=64, null=True, blank=True)

    class Meta:
        abstract = True

# Compatibility Aliases for existing code
BaseAccount = LedgerAccount
BaseFiscalPeriod = FinancialPeriod
BaseAccountingTransaction = BaseJournalLine
BaseBankTransaction = BasePayment
