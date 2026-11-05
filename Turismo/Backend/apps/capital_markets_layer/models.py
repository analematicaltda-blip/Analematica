import uuid
from django.db import models
from django.conf import settings

class Shareholder(models.Model):
    """
    Representa un accionista del holding (Fundadores, VCs, Empleados, Inversores).
    """
    class Type(models.TextChoices):
        FOUNDER = 'FOUNDER', 'Fundador'
        VC = 'VC', 'Venture Capital'
        PE = 'PE', 'Private Equity'
        ANGEL = 'ANGEL', 'Inversor Ángel'
        EMPLOYEE = 'EMPLOYEE', 'Empleado (ESOP)'
        INSTITUTIONAL = 'INSTITUTIONAL', 'Institucional'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=Type.choices)
    email = models.EmailField(unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class ShareClass(models.Model):
    """
    Clases de acciones con diferentes derechos y preferencias.
    """
    class Type(models.TextChoices):
        COMMON = 'COMMON', 'Acciones Ordinarias'
        PREFERRED = 'PREFERRED', 'Acciones Preferentes'
        SHADOW = 'SHADOW', 'Shadow Equity / Phantom'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100) # Ej: Series A Preferred
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.COMMON)

    liquidation_preference = models.DecimalField(max_digits=5, decimal_places=2, default=1.0) # Ej: 1x
    is_participating = models.BooleanField(default=False)
    dividend_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    votes_per_share = models.IntegerField(default=1)

    def __str__(self):
        return self.name

class EquityRound(models.Model):
    """
    Rondas de capitalización.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100) # Ej: Series A
    date = models.DateField()

    pre_money_valuation = models.DecimalField(max_digits=20, decimal_places=2)
    investment_amount = models.DecimalField(max_digits=20, decimal_places=2)
    post_money_valuation = models.DecimalField(max_digits=20, decimal_places=2)

    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

class ShareIssuance(models.Model):
    """
    Emisión específica de acciones a un accionista.
    """
    shareholder = models.ForeignKey(Shareholder, on_delete=models.CASCADE, related_name='issuances')
    share_class = models.ForeignKey(ShareClass, on_delete=models.PROTECT)
    round = models.ForeignKey(EquityRound, on_delete=models.SET_NULL, null=True, blank=True)

    shares_count = models.BigIntegerField()
    price_per_share = models.DecimalField(max_digits=18, decimal_places=4)
    issuance_date = models.DateField()

    certificate_number = models.CharField(max_length=50, unique=True, null=True, blank=True)

class DebtInstrument(models.Model):
    """
    Instrumentos de deuda y notas convertibles.
    """
    class Type(models.TextChoices):
        CONVERTIBLE_NOTE = 'CONVERTIBLE_NOTE', 'Nota Convertible'
        SAFE = 'SAFE', 'SAFE'
        VENTURE_DEBT = 'VENTURE_DEBT', 'Venture Debt'
        BANK_LOAN = 'BANK_LOAN', 'Préstamo Bancario'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    holder = models.ForeignKey(Shareholder, on_delete=models.PROTECT)
    type = models.CharField(max_length=50, choices=Type.choices)

    principal_amount = models.DecimalField(max_digits=20, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    # Para convertibles
    valuation_cap = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    maturity_date = models.DateField(null=True, blank=True)
    is_converted = models.BooleanField(default=False)

class SPV(models.Model):
    """
    Vehículos de Propósito Especial (Special Purpose Vehicles).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    purpose = models.TextField()
    jurisdiction = models.CharField(max_length=100) # Ej: Delaware, Cayman

    parent_holding = models.BooleanField(default=True)
    capital_committed = models.DecimalField(max_digits=20, decimal_places=2)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "SPV"
        verbose_name_plural = "SPVs"
