from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from apps.core_erp.base_models import BaseErpModel

class StateEntity(BaseErpModel):
    """
    Representa una institución u organismo estatal interoperable.
    """
    ENTITY_TYPES = (
        ('CENTRAL_BANK', 'National Central Bank'),
        ('TAX_AUTHORITY', 'Fiscal/Tax Platform'),
        ('REGULATORY_BODY', 'Sectoral Regulator'),
        ('FINANCIAL_INFRA', 'National Payments/Settlement Infra'),
        ('STRATEGIC_INFRA', 'Energy/Logistics State Infra'),
        ('MULTILATERAL', 'Multilateral Institution'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    country_code = models.CharField(max_length=3)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPES)

    is_certified = models.BooleanField(default=False, help_text="Holding is technically certified with this entity")
    compliance_score = models.DecimalField(max_digits=5, decimal_places=4, default=1.0)

    integration_config = models.JSONField(default=dict, help_text="Technical and legal parameters for integration")

    def __str__(self):
        return f"{self.name} [{self.country_code}]"

class IntegrationProtocol(BaseErpModel):
    """
    Protocolos de Interoperabilidad Estatal (SIPL).
    """
    PROTOCOL_LEVELS = (
        ('FINANCIAL', 'Payments & Liquidity Sync'),
        ('FISCAL', 'Real-time Tax Reporting'),
        ('IDENTITY', 'Sovereign ID Validation'),
        ('LOGISTICS', 'Strategic Supply Chain Interop'),
        ('ENERGY', 'Energy Grid Interaction'),
    )

    state_entity = models.ForeignKey(StateEntity, on_delete=models.CASCADE, related_name='protocols')
    name = models.CharField(max_length=100)
    protocol_level = models.CharField(max_length=20, choices=PROTOCOL_LEVELS)

    encryption_standard = models.CharField(max_length=50, default='AES-256-GCM')
    last_audit_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class SovereignComplianceNode(BaseErpModel):
    """
    Nodo de Cumplimiento Soberano e Inteligencia AI.
    IntegratedUtility = EconomicEfficiency + StateStabilityContribution - SovereignRisk
    """
    jurisdiction = models.CharField(max_length=3)
    reporting_frequency = models.CharField(max_length=20, default='DAILY')

    economic_efficiency = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    stability_contribution = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    sovereign_risk = models.DecimalField(max_digits=5, decimal_places=4, default=0.1)

    compliance_threshold = models.DecimalField(max_digits=5, decimal_places=4, default=0.95)
    last_report_hash = models.CharField(max_length=64, blank=True)

class InfrastructureProject(BaseErpModel):
    """
    Participación en Proyectos de Infraestructura Pública.
    """
    PROJECT_TYPES = (
        ('DIGITAL', 'National Data / Connectivity Network'),
        ('ENERGY', 'Power Grid / Green Energy'),
        ('LOGISTICS', 'Port / Hub / Strategic Transport'),
        ('FINTECH', 'National CBDC / Payment Infra'),
    )

    name = models.CharField(max_length=255)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES)
    lead_state_entity = models.ForeignKey(StateEntity, on_delete=models.CASCADE)

    holding_participation_share = models.DecimalField(max_digits=5, decimal_places=2)
    capital_committed = models.DecimalField(max_digits=20, decimal_places=4)

    status = models.CharField(max_length=20, default='PLANNING', choices=(
        ('PLANNING', 'Under Review'),
        ('ACTIVE', 'Operational Participation'),
        ('SUSPENDED', 'Sovereign Disengagement'),
    ))

class JointGovernanceCommittee(BaseErpModel):
    """
    Interfaz de Gobernanza Conjunta Holding-Estado (JGI).
    """
    name = models.CharField(max_length=255)
    state_entity = models.ForeignKey(StateEntity, on_delete=models.CASCADE)

    committee_members = models.JSONField(default=list, help_text="Mix of holding and state representatives")
    oversight_scope = models.TextField()

    intervention_protocol = models.JSONField(default=dict, help_text="Procedures for state intervention if necessary")
    is_active = models.BooleanField(default=True)
