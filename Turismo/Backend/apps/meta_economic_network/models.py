from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from apps.core_erp.base_models import BaseErpModel

class MetaEcosystem(BaseErpModel):
    """
    Representa un ecosistema económico (interno o externo) dentro de la red meta-económica.
    """
    ECOSYSTEM_TYPES = (
        ('INTERNAL', 'Internal Holding Ecosystem'),
        ('PARTNER', 'Strategic Partner Ecosystem'),
        ('GLOBAL_PLATFORM', 'Global Digital Platform'),
        ('SOVEREIGN', 'Sovereign Infrastructure Interface'),
        ('FINANCIAL_MARKET', 'Tokenized Financial Market'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    ecosystem_type = models.CharField(max_length=20, choices=ECOSYSTEM_TYPES)

    # Macro Metrics
    economic_output = models.DecimalField(max_digits=25, decimal_places=4, default=0)
    liquidity_depth = models.DecimalField(max_digits=25, decimal_places=4, default=0)
    risk_index = models.DecimalField(max_digits=5, decimal_places=4, default=0.1)

    # Meta-Network Data
    interdependence_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.5)
    regulatory_exposure = models.DecimalField(max_digits=5, decimal_places=4, default=0.2)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.ecosystem_type})"

class EcosystemInterdependence(BaseErpModel):
    """
    Rastrea las interdependencias cruzadas entre ecosistemas.
    """
    source_ecosystem = models.ForeignKey(MetaEcosystem, on_delete=models.CASCADE, related_name='outgoing_dependencies')
    target_ecosystem = models.ForeignKey(MetaEcosystem, on_delete=models.CASCADE, related_name='incoming_dependencies')

    dependency_weight = models.DecimalField(max_digits=5, decimal_places=4, help_text="Impact of target on source")
    criticality_level = models.CharField(max_length=20, choices=(
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('SYSTEMIC', 'Systemic'),
    ))

class InteroperabilityProtocol(BaseErpModel):
    """
    Protocolos estandarizados para la capa de interoperabilidad meta-económica.
    """
    PROTOCOL_TYPES = (
        ('VALUE_TRANSFER', 'Value Transfer Standard'),
        ('IDENTITY', 'Corporate Identity Validation'),
        ('COMPLIANCE', 'Automated Regulatory Compliance'),
        ('SETTLEMENT', 'Financial Settlement Protocol'),
        ('DATA_SHARING', 'Secure Data Exchange'),
    )

    name = models.CharField(max_length=100)
    protocol_type = models.CharField(max_length=20, choices=PROTOCOL_TYPES)
    version = models.CharField(max_length=20)
    specification_hash = models.CharField(max_length=64, unique=True)

    is_certified = models.BooleanField(default=False)

class GlobalUtilityMetric(BaseErpModel):
    """
    Métrica de Utilidad Global (Fase 20.5).
    GlobalUtility = Sum(Contribution - Externality - SystemicRisk)
    """
    ecosystem = models.ForeignKey(MetaEcosystem, on_delete=models.CASCADE, related_name='utility_history')
    period = models.CharField(max_length=20, help_text="YYYY-MM or YYYY-QQ")

    contribution_score = models.DecimalField(max_digits=20, decimal_places=4)
    externality_cost = models.DecimalField(max_digits=20, decimal_places=4)
    risk_penalty = models.DecimalField(max_digits=20, decimal_places=4)

    net_global_utility = models.DecimalField(max_digits=20, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)

class MetaLiquidityPool(BaseErpModel):
    """
    Pooling dinámico de capital entre ecosistemas.
    """
    name = models.CharField(max_length=255)
    participating_ecosystems = models.ManyToManyField(MetaEcosystem, related_name='liquidity_pools')

    total_liquidity = models.DecimalField(max_digits=25, decimal_places=4, default=0)
    stabilization_buffer = models.DecimalField(max_digits=25, decimal_places=4, default=0)

    is_emergency_active = models.BooleanField(default=False)
