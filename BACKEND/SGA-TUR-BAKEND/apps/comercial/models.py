import uuid
from django.db import models

class Lead(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'New'
        QUALIFIED = 'qualified', 'Qualified'
        REJECTED = 'rejected', 'Rejected'
        CONVERTED = 'converted', 'Converted'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=100, default='organic')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    score = models.IntegerField(default=0)
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'comercial'

class Plan(models.Model):
    """
    Modelo unificado de Planes (Fase 3).
    Soporta tiers, add-ons y versionado.
    """
    class TargetUserType(models.TextChoices):
        GOVERNMENT = 'GOVERNMENT', 'Gobierno'
        PROVIDER = 'PROVIDER', 'Prestador'

    class BillingSchema(models.TextChoices):
        FLAT = 'FLAT', 'Precio Fijo'
        TIERED = 'TIERED', 'Por Tramos (Escalonado)'
        PER_UNIT = 'PER_UNIT', 'Por Unidad de Uso'

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50)
    version = models.IntegerField(default=1)
    description = models.TextField(blank=True)

    billing_schema = models.CharField(
        max_length=20,
        choices=BillingSchema.choices,
        default=BillingSchema.FLAT
    )

    monthly_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    yearly_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Límites Base
    storage_limit_gb = models.IntegerField(default=5)
    user_limit = models.IntegerField(default=1)
    transaction_limit = models.IntegerField(default=100)

    target_user_type = models.CharField(
        max_length=20,
        choices=TargetUserType.choices,
        default=TargetUserType.PROVIDER
    )

    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Configuraciones extra del plan")

    def __str__(self):
        return f"{self.name} v{self.version} ({self.code})"

    class Meta:
        app_label = 'comercial'
        unique_together = ('code', 'version')

class PlanTier(models.Model):
    """Define tramos de precios para planes escalonados."""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='tiers')
    from_unit = models.IntegerField()
    to_unit = models.IntegerField(null=True, blank=True) # null = infinito
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        app_label = 'comercial'
        ordering = ['from_unit']

class AddOn(models.Model):
    """Funcionalidades o recursos extra que se pueden comprar por separado."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)
    monthly_price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'comercial'

class Opportunity(models.Model):
    class Stage(models.TextChoices):
        PROSPECTING = 'prospecting', 'Prospecting'
        WON = 'won', 'Won'
        LOST = 'lost', 'Lost'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='opportunities')
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.PROSPECTING)
    estimated_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        app_label = 'comercial'

class Subscription(models.Model):
    """
    Modelo unificado de Suscripciones (Fase 3).
    Gestiona el ciclo de vida automático.
    """
    class Status(models.TextChoices):
        TRIAL = 'TRIAL', 'Periodo de Prueba'
        ACTIVE = 'ACTIVE', 'Activa'
        PAST_DUE = 'PAST_DUE', 'Mora (Pendiente)'
        SUSPENDED = 'SUSPENDED', 'Suspendida'
        CANCELED = 'CANCELED', 'Cancelada'

    class BillingCycle(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Mensual'
        YEARLY = 'YEARLY', 'Anual'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=100, unique=True)
    perfil_ref_id = models.UUIDField(db_index=True, null=True, blank=True)

    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    add_ons = models.ManyToManyField(AddOn, blank=True, related_name='subscriptions')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIAL)
    billing_cycle = models.CharField(max_length=20, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    next_billing_date = models.DateField(null=True, blank=True)
    last_billing_date = models.DateField(null=True, blank=True)

    cancel_at_period_end = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Métricas de salud para el RetentionEngine
    health_score = models.FloatField(default=1.0)
    last_activity = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sub: {self.tenant_id} - {self.plan.name} ({self.status})"

    class Meta:
        app_label = 'comercial'

class PricingRule(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='pricing_rules')
    extra_gb_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        app_label = 'comercial'

class UsageMetric(models.Model):
    tenant_id = models.CharField(max_length=100)
    metric_type = models.CharField(max_length=50)
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    period_start = models.DateField()
    period_end = models.DateField()

    class Meta:
        app_label = 'comercial'

class BillingCycle(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='billing_cycles')
    cycle_start = models.DateField()
    cycle_end = models.DateField()
    amount_calculated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        app_label = 'comercial'
