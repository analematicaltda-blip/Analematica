from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
from apps.core_erp.base_models import BaseErpModel

class GovernanceBody(BaseErpModel):
    """
    Representa un órgano institucional dentro del marco de gobernanza transnacional.
    """
    BODY_TYPES = (
        ('TSC', 'Transnational Strategic Council'),
        ('MRB', 'Multi-Jurisdictional Regulatory Board'),
        ('AOA', 'Algorithmic Oversight Authority'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    body_type = models.CharField(max_length=10, choices=BODY_TYPES)

    jurisdiction_coverage = models.JSONField(default=list, help_text="List of country codes involved")
    is_active = models.BooleanField(default=True)

    governance_level = models.IntegerField(choices=((1, 'Operational'), (2, 'Regulatory'), (3, 'Strategic')))

    mandate_description = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.body_type})"

class GovernanceMember(BaseErpModel):
    """
    Representante (Holding, Estado u Observador) dentro de un órgano de gobernanza.
    """
    MEMBER_ROLES = (
        ('HOLDING_REP', 'Holding Representative'),
        ('STATE_REP', 'Sovereign/State Representative'),
        ('INDEPENDENT_OBSERVER', 'Independent Technical Observer'),
        ('ETHICS_COMMITTEE', 'Ethics Committee Member'),
    )

    body = models.ForeignKey(GovernanceBody, on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=25, choices=MEMBER_ROLES)
    organization_represented = models.CharField(max_length=255)

    is_certified = models.BooleanField(default=False)
    last_review_date = models.DateTimeField(auto_now=True)

class AlgorithmicAudit(BaseErpModel):
    """
    Auditoría técnica de modelos algorítmicos (Fase 22.5 - AOA).
    """
    AUDIT_STATUS = (
        ('PENDING', 'Pending Technical Review'),
        ('APPROVED', 'Certified for Systemic Stability'),
        ('REJECTED', 'Bias or Instability Detected'),
        ('RESTRICTED', 'Active with Operational Limits'),
    )

    target_component = models.CharField(max_length=100, help_text="e.g., IncentiveMatrix, CEOE, ARIE")
    version_hash = models.CharField(max_length=64)
    audit_date = models.DateTimeField(auto_now_add=True)

    stability_index = models.DecimalField(max_digits=5, decimal_places=4)
    bias_score = models.DecimalField(max_digits=5, decimal_places=4)

    status = models.CharField(max_length=20, choices=AUDIT_STATUS, default='PENDING')
    audit_report_url = models.URLField(blank=True)

class DisputeCase(BaseErpModel):
    """
    Mecanismo de Resolución de Conflictos Transnacionales (Fase 22.5).
    """
    CASE_TYPES = (
        ('REGULATORY_FRICTION', 'Cross-Border Regulatory Conflict'),
        ('CONTRACTUAL_DISPUTE', 'Multi-Jurisdiction Agreement Dispute'),
        ('SYSTEMIC_RISK_EVENT', 'Shared Systemic Crisis Disagreement'),
    )

    title = models.CharField(max_length=255)
    case_type = models.CharField(max_length=25, choices=CASE_TYPES)
    governance_body = models.ForeignKey(GovernanceBody, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, default='OPEN', choices=(
        ('OPEN', 'Under Arbitration'),
        ('MEDIATION', 'Negotiation Phase'),
        ('RESOLVED', 'Resolution Applied'),
        ('ESCALATED', 'Escalated to Strategic Council'),
    ))

    resolution_details = models.TextField(blank=True)

class GovernanceStabilityMetric(BaseErpModel):
    """
    Métricas de Estabilidad Institucional (Fase 22.7).
    f(SovereignRespect, Transparency, Accountability, SystemicRiskControl)
    """
    body = models.ForeignKey(GovernanceBody, on_delete=models.CASCADE, related_name='stability_history')
    period = models.CharField(max_length=20)

    sovereign_respect_score = models.DecimalField(max_digits=5, decimal_places=4)
    transparency_index = models.DecimalField(max_digits=5, decimal_places=4)
    accountability_score = models.DecimalField(max_digits=5, decimal_places=4)

    net_stability_index = models.DecimalField(max_digits=5, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)
