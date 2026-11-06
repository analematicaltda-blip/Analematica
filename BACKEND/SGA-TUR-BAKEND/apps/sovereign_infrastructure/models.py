from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from apps.core_erp.base_models import BaseErpModel

class JurisdictionalNode(BaseErpModel):
    """
    Representa una entidad legal en una jurisdicción específica para redundancia soberana.
    """
    NODE_LEVELS = (
        ('ROOT', 'Global Strategic Entity (Holding Root)'),
        ('REGIONAL', 'Regional Control Entity'),
        ('SUBSIDIARY', 'Operational Subsidiary'),
        ('ASSET_VEHICLE', 'Asset-Level SPV'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=3, help_text="ISO 3166-1 alpha-3")
    level = models.CharField(max_length=20, choices=NODE_LEVELS)

    parent_node = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_nodes')

    legal_structure_type = models.CharField(max_length=100, help_text="LLC, SA, Trust, etc.")
    is_active = models.BooleanField(default=True)

    # Resiliencia Score
    stability_index = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)
    political_risk_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0)

    def __str__(self):
        return f"{self.name} [{self.country_code}] ({self.level})"

class RegulatoryProfile(BaseErpModel):
    """
    Perfil regulatorio de una jurisdicción monitoreado por el ARIE.
    """
    node = models.OneToOneField(JurisdictionalNode, on_delete=models.CASCADE, related_name='regulatory_profile')

    tax_regime = models.JSONField(default=dict)
    capital_controls = models.BooleanField(default=False)
    reporting_requirements = models.JSONField(default=list)

    compliance_score = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)
    last_update = models.DateTimeField(auto_now=True)

    alert_threshold = models.DecimalField(max_digits=5, decimal_places=4, default=0.7, help_text="Stability threshold to trigger migration")

class CapitalShield(BaseErpModel):
    """
    Blindaje de Capital Multi-Soberano. Distribución de activos por riesgo.
    """
    ASSET_TYPES = (
        ('TRADITIONAL', 'Fiat / Traditional Financial'),
        ('TOKENIZED', 'On-chain / Programmable Capital'),
        ('COMMODITY', 'Physical Assets / Commodities'),
        ('INTELLECTUAL', 'IP / Intangible Assets'),
    )

    node = models.ForeignKey(JurisdictionalNode, on_delete=models.CASCADE, related_name='capital_shields')
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    currency = models.CharField(max_length=10)
    current_value = models.DecimalField(max_digits=20, decimal_places=4)

    liquidity_ratio = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)
    risk_exposure = models.DecimalField(max_digits=5, decimal_places=4, default=0.1)

    is_locked = models.BooleanField(default=False, help_text="Locked by regulatory or security event")

class DigitalInfraBackup(BaseErpModel):
    """
    Infraestructura Digital Independiente. Registro de redundancia técnica.
    """
    INFRA_TYPES = (
        ('CLOUD', 'Cloud Provider Region'),
        ('ON_PREM', 'Regional Data Center'),
        ('DECENTRALIZED', 'Distributed Validation Node'),
    )

    name = models.CharField(max_length=255)
    provider = models.CharField(max_length=100)
    infra_type = models.CharField(max_length=20, choices=INFRA_TYPES)
    jurisdiction = models.CharField(max_length=3)

    sync_status = models.CharField(max_length=20, default='ACTIVE')
    data_redundancy_level = models.IntegerField(default=3)
    last_health_check = models.DateTimeField(null=True, blank=True)

class CorporateConstitution(BaseErpModel):
    """
    Constitución Interna Corporativa (Gobernanza Soberana).
    Reglas fundamentales inmutables.
    """
    title = models.CharField(max_length=255)
    constitutional_article = models.TextField()
    immutable_hash = models.CharField(max_length=64, unique=True)

    autonomy_limit = models.DecimalField(max_digits=5, decimal_places=4, default=0.5, help_text="Max algorithmic autonomy before human intervention")
    intervention_protocol = models.JSONField(default=dict)

    version = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
