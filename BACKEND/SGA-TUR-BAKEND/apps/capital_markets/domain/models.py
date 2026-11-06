from django.db import models
from apps.core_erp.base_models import TenantAwareModel
import uuid

class CapitalStructure(TenantAwareModel):
    """
    Consolidated view of the global capital structure and WACC.
    """
    wacc = models.DecimalField(max_digits=5, decimal_places=4, default=0)
    debt_to_equity = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    total_equity = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    total_debt = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    # Phase 17: Tokenized Capital
    tokenized_equity = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tokenized_debt = models.DecimalField(max_digits=20, decimal_places=2, default=0)

    internal_credit_rating = models.CharField(max_length=10, default='BBB')
    target_leverage = models.DecimalField(max_digits=5, decimal_places=4, default=0.4)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'capital_markets'

class DebtInstrument(TenantAwareModel):
    """
    Management of corporate bonds and structured debt.
    """
    class InstrumentType(models.TextChoices):
        BOND = 'BOND', 'Corporate Bond'
        GREEN_BOND = 'GREEN_BOND', 'Green Bond'
        NOTE = 'NOTE', 'Structured Note'
        PRIVATE_DEBT = 'PRIVATE_DEBT', 'Private Debt'

    instrument_type = models.CharField(max_length=50, choices=InstrumentType.choices)
    isin_code = models.CharField(max_length=12, blank=True, null=True)

    principal_amount = models.DecimalField(max_digits=20, decimal_places=2)
    coupon_rate = models.DecimalField(max_digits=5, decimal_places=4)
    maturity_date = models.DateField()

    status = models.CharField(max_length=20, choices=[('ISSUED','Issued'), ('MATURED','Matured'), ('REDEEMED','Redeemed')], default='ISSUED')
    covenants = models.JSONField(default=dict, blank=True)

    class Meta:
        app_label = 'capital_markets'

class EquityInstrument(TenantAwareModel):
    """
    Management of shares and strategic equity positions.
    """
    instrument_name = models.CharField(max_length=255)
    total_shares = models.DecimalField(max_digits=20, decimal_places=2)
    par_value = models.DecimalField(max_digits=20, decimal_places=2)

    market_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    dividend_yield = models.DecimalField(max_digits=5, decimal_places=4, default=0)

    class Meta:
        app_label = 'capital_markets'

class MarketRating(TenantAwareModel):
    """
    Internal rating simulation against market spreads.
    """
    agency_source = models.CharField(max_length=100) # e.g. Internal, Moody's Mock
    rating_score = models.CharField(max_length=10)

    default_probability = models.DecimalField(max_digits=5, decimal_places=4)
    market_spread_bps = models.IntegerField()

    effective_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'capital_markets'

class StructuredDeal(TenantAwareModel):
    """
    Asset-backed securitization and SPV management.
    """
    deal_name = models.CharField(max_length=255)
    underlying_asset_type = models.CharField(max_length=100) # e.g. Operational Bookings

    tranche_structure = models.JSONField()
    spv_legal_name = models.CharField(max_length=255)

    total_size = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=20, default='PROPOSAL')

    class Meta:
        app_label = 'capital_markets'
