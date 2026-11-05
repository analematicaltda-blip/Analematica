from django.db import models
import uuid

class CorporateHolding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    holding_name = models.CharField(max_length=255, unique=True)
    jurisdiction = models.CharField(max_length=100) # e.g., Delaware, Cayman, Colombia
    parent_holding = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_holdings')
    controlling_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    board_structure = models.JSONField(default=dict)
    capital_structure = models.JSONField(default=dict)
    reporting_currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.holding_name

class LegalEntity(models.Model):
    ENTITY_TYPES = [
        ('OPERATING', 'Operating Entity (OpCo)'),
        ('IP_CO', 'Intellectual Property Holding (IP Co)'),
        ('INFRA_CO', 'Infrastructure Entity'),
        ('COMMERCIAL', 'Commercial/Sales Entity'),
        ('TREASURY', 'Treasury/Capital Management'),
        ('BRAND', 'Brand Holding'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    tax_id = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)
    parent_holding = models.ForeignKey(CorporateHolding, on_delete=models.CASCADE, related_name='entities')
    functional_currency = models.CharField(max_length=3, default='USD')
    fiscal_calendar = models.CharField(max_length=50, default='Standard') # Jan-Dec

    # Reference to the actual Company in core_erp if mapped
    core_company_id = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return f"{self.entity_name} ({self.entity_type})"

class IntercompanyTransaction(models.Model):
    TX_TYPES = [
        ('BILLING', 'Intercompany Billing'),
        ('LOAN', 'Intercompany Loan'),
        ('TRANSFER', 'Capital Transfer'),
        ('ROYALTY', 'IP Royalty'),
        ('COST_SHARE', 'Cost Sharing'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_entity = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, related_name='outgoing_tx')
    destination_entity = models.ForeignKey(LegalEntity, on_delete=models.CASCADE, related_name='incoming_tx')
    tx_type = models.CharField(max_length=20, choices=TX_TYPES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=3)
    description = models.TextField()
    is_mirrored = models.BooleanField(default=False) # If both sides posted in ERP
    mirror_reference = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TransferPricingRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule_name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=LegalEntity.ENTITY_TYPES)
    dest_type = models.CharField(max_length=20, choices=LegalEntity.ENTITY_TYPES)
    markup_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

class OwnershipRegistry(models.Model):
    """Tracks historical ownership percentages."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(CorporateHolding, on_delete=models.CASCADE)
    entity = models.ForeignKey(LegalEntity, on_delete=models.CASCADE)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    as_of_date = models.DateField()
