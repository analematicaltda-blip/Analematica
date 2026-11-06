"""Additive, tenant-scoped audience, media variants and durable publication outbox."""
from sqlalchemy import Column,Integer,String,Text,Boolean,DateTime,ForeignKey,UniqueConstraint
from sqlalchemy.sql import func
from .base import Base

class CampaignContact(Base):
    __tablename__='campaign_contacts'
    __table_args__=(UniqueConstraint('scope','provider','address',name='uq_campaign_contact'),)
    id=Column(String(36),primary_key=True)
    scope=Column(String(64),nullable=False,index=True)
    provider=Column(String(24),nullable=False)
    address=Column(String(254),nullable=False)
    name=Column(String(150),nullable=False,default='')
    consent_source=Column(String(250),nullable=False)
    subscribed=Column(Boolean,nullable=False,default=True)
    created_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

class Campaign(Base):
    __tablename__='campaigns'
    __table_args__=(UniqueConstraint('scope','idempotency_key',name='uq_campaign_request'),)
    id=Column(String(36),primary_key=True)
    scope=Column(String(64),nullable=False,index=True)
    idempotency_key=Column(String(36),nullable=False)
    request_hash=Column(String(64),nullable=False)
    asset_id=Column(String(36),ForeignKey('workspace_assets.id'),nullable=False)
    title=Column(String(100),nullable=False)
    description=Column(Text,nullable=False,default='')
    state=Column(String(24),nullable=False,default='draft')
    scheduled_at=Column(DateTime(timezone=True),nullable=False,index=True)
    timezone=Column(String(80),nullable=False)
    created_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)
    approved_by=Column(Integer,ForeignKey('usuarios.id'))
    created_at=Column(DateTime(timezone=True),server_default=func.now())

class CampaignTarget(Base):
    __tablename__='campaign_targets'
    __table_args__=(UniqueConstraint('campaign_id','provider','contact_key',name='uq_campaign_target'),)
    id=Column(String(36),primary_key=True)
    campaign_id=Column(String(36),ForeignKey('campaigns.id'),nullable=False,index=True)
    provider=Column(String(24),nullable=False)
    contact_key=Column(String(36),nullable=False,default='account')
    contact_id=Column(String(36),ForeignKey('campaign_contacts.id'))
    channel_fingerprint=Column(String(64))
    variant_id=Column(String(36),ForeignKey('workspace_assets.id'))
    state=Column(String(24),nullable=False,default='draft',index=True)
    next_at=Column(DateTime(timezone=True),nullable=False,index=True)
    claimed_at=Column(DateTime(timezone=True))
    phase=Column(Integer,nullable=False,default=0)
    provider_state=Column(Text,nullable=False,default='{}')
    options=Column(Text,nullable=False,default='{}')
    remote_id=Column(String(200))
    detail=Column(String(250),nullable=False,default='')
    quota_charged=Column(Boolean,nullable=False,default=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

class CampaignVariant(Base):
    __tablename__='campaign_variants'
    __table_args__=(UniqueConstraint('source_id','profile',name='uq_campaign_variant'),)
    id=Column(Integer,primary_key=True)
    source_id=Column(String(36),ForeignKey('workspace_assets.id'),nullable=False)
    profile=Column(String(24),nullable=False)
    asset_id=Column(String(36),ForeignKey('workspace_assets.id'),nullable=False)

class CampaignScheduler(Base):
    __tablename__='campaign_scheduler'
    id=Column(String(32),primary_key=True)
    last_seen=Column(DateTime(timezone=True),nullable=False)

class CampaignSetting(Base):
    __tablename__='campaign_settings'
    id=Column(String(40),primary_key=True)
    value=Column(Text,nullable=False)
