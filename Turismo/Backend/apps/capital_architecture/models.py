from django.db import models
import uuid
from django.utils import timezone

class Shareholder(models.Model):
    TYPES = [('INDIVIDUAL', 'Individual'), ('ENTITY', 'Corporate Entity'), ('VC', 'Venture Capital')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    shareholder_type = models.CharField(max_length=20, choices=TYPES)
    email = models.EmailField()
    is_founder = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class EquityClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_name = models.CharField(max_length=100) # Common, Series Seed, Series A
    liquidation_priority = models.IntegerField(default=1) # Lower = Higher priority
    multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00) # Liquidation multiplier
    is_preferred = models.BooleanField(default=False)
    has_voting_rights = models.BooleanField(default=True)

    def __str__(self):
        return self.class_name

class ShareCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE, related_name='certificates')
    equity_class = models.ForeignKey(EquityClass, on_delete=models.CASCADE)
    quantity = models.BigIntegerField()
    issue_date = models.DateField()
    price_per_share = models.DecimalField(max_digits=20, decimal_places=4)
    vesting_start_date = models.DateField(null=True, blank=True)
    vesting_months = models.IntegerField(default=48)
    cliff_months = models.IntegerField(default=12)

class SAFE(models.Model):
    """Simple Agreement for Future Equity."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE)
    investment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    valuation_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.80) # 20% discount = 0.80
    is_converted = models.BooleanField(default=False)

class ConvertibleNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE)
    principal_amount = models.DecimalField(max_digits=20, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2) # Annual %
    valuation_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    maturity_date = models.DateField()
