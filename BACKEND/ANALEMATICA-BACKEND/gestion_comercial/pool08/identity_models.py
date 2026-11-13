"""Additive native commercial controls; no existing user/role model is changed."""
from django.db import models

class CommercialGrant(models.Model):
    id = models.CharField(max_length=36, primary_key=True, serialize=False)
    tenant_ref = models.CharField(max_length=96)
    revision = models.PositiveIntegerField()
    digest = models.CharField(max_length=64)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    subject_ref = models.CharField(max_length=80)
    role_fingerprint = models.CharField(max_length=64)
    capabilities = models.JSONField(default=list)
    granted_by_ref = models.CharField(max_length=80)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        app_label = 'admin_plataforma'
        db_table = "ana_commercial_grant"
        constraints = [models.UniqueConstraint(fields=['tenant_ref', 'subject_ref'], name="ana_comm_grant_scope")]

class CommercialConsent(models.Model):
    id = models.CharField(max_length=36, primary_key=True, serialize=False)
    tenant_ref = models.CharField(max_length=96)
    revision = models.PositiveIntegerField()
    digest = models.CharField(max_length=64)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    customer_ref = models.CharField(max_length=96)
    channel = models.CharField(max_length=32)
    purpose = models.CharField(max_length=32)
    evidence_digest = models.CharField(max_length=64)
    recorded_by_ref = models.CharField(max_length=80)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        app_label = 'admin_plataforma'
        db_table = "ana_commercial_consent"
        constraints = [models.UniqueConstraint(fields=['tenant_ref', 'customer_ref', 'channel', 'purpose'], name="ana_comm_consent_scope")]

class CommercialIdentityAlias(models.Model):
    id = models.CharField(max_length=36, primary_key=True, serialize=False)
    tenant_ref = models.CharField(max_length=96)
    revision = models.PositiveIntegerField()
    digest = models.CharField(max_length=64)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    local_actor_ref = models.CharField(max_length=80)
    external_system = models.CharField(max_length=32)
    external_tenant_ref = models.CharField(max_length=96)
    external_actor_ref = models.CharField(max_length=96)
    evidence_digest = models.CharField(max_length=64)
    recorded_by_ref = models.CharField(max_length=80)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        app_label = 'admin_plataforma'
        db_table = "ana_commercial_alias"
        constraints = [models.UniqueConstraint(fields=['tenant_ref', 'local_actor_ref', 'external_system', 'external_tenant_ref', 'external_actor_ref'], name="ana_comm_alias_scope")]

class CommercialPolicyEvent(models.Model):
    id = models.CharField(max_length=36, primary_key=True, serialize=False)
    tenant_ref = models.CharField(max_length=96)
    revision = models.PositiveIntegerField()
    digest = models.CharField(max_length=64)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    actor_ref = models.CharField(max_length=80)
    operation = models.CharField(max_length=32)
    request_digest = models.CharField(max_length=64)
    result = models.JSONField(default=dict)
    class Meta:
        app_label = 'admin_plataforma'
        db_table = "ana_commercial_event"
