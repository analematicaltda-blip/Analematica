"""Additive SGA-CD commercial controls; existing roles and tables are preserved."""
from sqlalchemy import Column, String, Integer, DateTime, JSON, UniqueConstraint
from app.models.base import Base

class CommercialGrant(Base):
    __tablename__ = "sga_commercial_grant"
    __table_args__ = (UniqueConstraint('tenant_ref','subject_ref', name="sga_comm_grant_scope"),)
    id = Column(String(36), primary_key=True)
    tenant_ref = Column(String(96), nullable=False)
    revision = Column(Integer, nullable=False)
    digest = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    subject_ref = Column(String(80), nullable=False)
    role_fingerprint = Column(String(64), nullable=False)
    capabilities = Column(JSON, nullable=False)
    granted_by_ref = Column(String(80), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

class CommercialConsent(Base):
    __tablename__ = "sga_commercial_consent"
    __table_args__ = (UniqueConstraint('tenant_ref','customer_ref','channel','purpose', name="sga_comm_consent_scope"),)
    id = Column(String(36), primary_key=True)
    tenant_ref = Column(String(96), nullable=False)
    revision = Column(Integer, nullable=False)
    digest = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    customer_ref = Column(String(96), nullable=False)
    channel = Column(String(32), nullable=False)
    purpose = Column(String(32), nullable=False)
    evidence_digest = Column(String(64), nullable=False)
    recorded_by_ref = Column(String(80), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

class CommercialIdentityAlias(Base):
    __tablename__ = "sga_commercial_alias"
    __table_args__ = (UniqueConstraint('tenant_ref','local_actor_ref','external_system','external_tenant_ref','external_actor_ref', name="sga_comm_alias_scope"),)
    id = Column(String(36), primary_key=True)
    tenant_ref = Column(String(96), nullable=False)
    revision = Column(Integer, nullable=False)
    digest = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    local_actor_ref = Column(String(80), nullable=False)
    external_system = Column(String(32), nullable=False)
    external_tenant_ref = Column(String(96), nullable=False)
    external_actor_ref = Column(String(96), nullable=False)
    evidence_digest = Column(String(64), nullable=False)
    recorded_by_ref = Column(String(80), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

class CommercialPolicyEvent(Base):
    __tablename__ = "sga_commercial_event"
    id = Column(String(36), primary_key=True)
    tenant_ref = Column(String(96), nullable=False)
    revision = Column(Integer, nullable=False)
    digest = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    actor_ref = Column(String(80), nullable=False)
    operation = Column(String(32), nullable=False)
    request_digest = Column(String(64), nullable=False)
    result = Column(JSON, nullable=False)
