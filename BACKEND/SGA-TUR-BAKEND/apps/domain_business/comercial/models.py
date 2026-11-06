from django.db import models
from django.conf import settings
from apps.core_erp.base_models import BaseErpModel, BaseInvoice, TenantAwareModel

class CommercialOperation(TenantAwareModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        INVOICED = 'INVOICED', 'Invoiced'
        VOIDED = 'VOIDED', 'Voided'

    Estado = Status # Compatibility Alias

    class OperationType(models.TextChoices):
        SALE = 'SALE', 'Sale'
        CONTRACT = 'CONTRACT', 'Contract'

    customer_id = models.UUIDField()
    operation_type = models.CharField(max_length=20, choices=OperationType.choices, default=OperationType.SALE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    taxes = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Commercial Operation"
        app_label = 'domain_business'

class OperationItem(TenantAwareModel):
    operation = models.ForeignKey(CommercialOperation, on_delete=models.CASCADE, related_name='items')
    product_id = models.UUIDField()
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        app_label = 'domain_business'

class SalesInvoice(BaseInvoice):
    class TaxStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'

    operation = models.OneToOneField(CommercialOperation, on_delete=models.PROTECT, related_name='invoice')
    tax_status = models.CharField(max_length=20, choices=TaxStatus.choices, default=TaxStatus.PENDING)
    fiscal_code = models.CharField(max_length=255, null=True, blank=True) # CUFE equivalent

    class Meta:
        app_label = 'domain_business'

class InvoiceItem(TenantAwareModel):
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='items')
    product_id = models.UUIDField()
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    subtotal = models.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        app_label = 'domain_business'

# Compatibility Aliases
OperacionComercial = CommercialOperation
ItemOperacionComercial = OperationItem
FacturaVenta = SalesInvoice
ItemFactura = InvoiceItem
