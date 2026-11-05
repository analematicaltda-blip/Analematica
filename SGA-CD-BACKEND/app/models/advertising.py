"""Advertising setup is separate from organic publishing and tenant credentials."""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from .base import Base

class MetaAdsApp(Base):
    __tablename__ = 'meta_ads_app'
    id = Column(Integer, primary_key=True)
    app_id = Column(String(40), nullable=False)
    api_version = Column(String(10), nullable=False)
    login_config_id = Column(String(40), nullable=False, default='')
    redirect_uris = Column(Text, nullable=False)
    encrypted_secret = Column(Text, nullable=False)
    revision = Column(Integer, nullable=False, default=1)
    configured_by = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MetaAdsAuthorization(Base):
    __tablename__ = 'meta_ads_authorizations'
    scope = Column(String(64), primary_key=True)
    app_id = Column(String(40), nullable=False)
    encrypted_token = Column(Text, nullable=False)
    principal_id = Column(String(40), nullable=False)
    permissions = Column(Text, nullable=False, default='[]')
    expires_at = Column(DateTime(timezone=True))
    invalid_reason = Column(String(40))
    account = Column(Text, nullable=False, default='{}')
    connected_by = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    verified_at = Column(DateTime(timezone=True), server_default=func.now())

class MetaAdsOAuthState(Base):
    __tablename__ = 'meta_ads_oauth_states'
    state_hash = Column(String(64), primary_key=True)
    browser_hash = Column(String(64), nullable=False)
    scope = Column(String(64), nullable=False, index=True)
    actor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    app_revision = Column(Integer, nullable=False)
    redirect_uri = Column(String(500), nullable=False)
    return_path = Column(String(200), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))
    outcome = Column(String(40))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AdvertisingProfile(Base):
    __tablename__ = 'advertising_profiles'
    __table_args__ = (UniqueConstraint('scope', 'network', name='uq_advertising_profile'),)
    id = Column(Integer, primary_key=True)
    scope = Column(String(64), nullable=False)
    network = Column(String(20), nullable=False)
    public_url = Column(String(400), nullable=False)
    handle = Column(String(80), nullable=False, default='')
    declared_id = Column(String(40), nullable=False, default='')
    verified_id = Column(String(40))
    verified_at = Column(DateTime(timezone=True))

class AdvertisingDraft(Base):
    __tablename__ = 'advertising_drafts'
    id = Column(String(36), primary_key=True)
    scope = Column(String(64), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    request_hash = Column(String(64), nullable=False)
    objective = Column(String(40), nullable=False)
    description = Column(Text, nullable=False, default='')
    account_id = Column(String(60))
    planned_budget = Column(String(40))
    currency = Column(String(3))
    status = Column(String(30), nullable=False, default='local_draft')
    created_by = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InstagramLoginConfig(Base):
    __tablename__ = 'instagram_login_config'
    id = Column(Integer, primary_key=True)
    config_id = Column(String(40), nullable=False)
    revision = Column(Integer, nullable=False, default=1)

class InstagramAuthorization(Base):
    __tablename__ = 'instagram_authorizations'
    scope = Column(String(64), primary_key=True)
    app_id = Column(String(40), nullable=False)
    encrypted_token = Column(Text, nullable=False)
    permissions = Column(Text, nullable=False, default='[]')
    expires_at = Column(DateTime(timezone=True))
    account = Column(Text, nullable=False, default='{}')
    connected_by = Column(Integer, ForeignKey('usuarios.id'), nullable=False)

class InstagramOAuthState(Base):
    __tablename__ = 'instagram_oauth_states'
    state_hash = Column(String(64), primary_key=True)
    browser_hash = Column(String(64), nullable=False)
    scope = Column(String(64), nullable=False)
    actor_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    app_revision = Column(Integer, nullable=False)
    config_revision = Column(Integer, nullable=False)
    redirect_uri = Column(String(500), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))

class MetaWebhookConfig(Base):
    __tablename__ = 'meta_webhook_config'
    id = Column(Integer, primary_key=True)
    encrypted_verify_token = Column(Text, nullable=False)
    accepted_ids = Column(Text, nullable=False, default='[]')

class MetaWebhookEvent(Base):
    __tablename__ = 'meta_webhook_events'
    id = Column(String(64), primary_key=True)
    scope = Column(String(64), nullable=False, default='platform')
    object_type = Column(String(40), nullable=False)
    encrypted_payload = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default='received')
    received_at = Column(DateTime(timezone=True), server_default=func.now())
