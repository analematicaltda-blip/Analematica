"""Additive tables for tenant delegation, CRM and Node 6 artifact ownership."""
from sqlalchemy import Column,Integer,String,Boolean,DateTime,Text,ForeignKey,UniqueConstraint
from sqlalchemy.sql import func
from .base import Base

class WorkspaceGrant(Base):
    __tablename__='workspace_grants'
    __table_args__=(UniqueConstraint('tenant_id','user_id','permission',name='uq_workspace_grant'),)
    id=Column(Integer,primary_key=True)
    tenant_id=Column(Integer,ForeignKey('inquilinos.id'),nullable=False,index=True)
    user_id=Column(Integer,ForeignKey('usuarios.id'),nullable=False,index=True)
    permission=Column(String(32),nullable=False)
    enabled=Column(Boolean,nullable=False,default=False)
    granted_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)
    updated_at=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())

class WorkspaceAsset(Base):
    __tablename__='workspace_assets'
    id=Column(String(36),primary_key=True)
    scope=Column(String(64),nullable=False,index=True)
    filename=Column(String(80),nullable=False,unique=True)
    kind=Column(String(16),nullable=False)
    title=Column(String(120),nullable=False,default='')
    publish_status=Column(String(20),nullable=False,default='new')
    publish_video_id=Column(String(80))
    created_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

class WorkspaceLead(Base):
    __tablename__='workspace_leads'
    id=Column(String(36),primary_key=True)
    scope=Column(String(64),nullable=False,index=True)
    name=Column(String(150),nullable=False)
    email=Column(String(254),nullable=False,default='')
    stage=Column(String(20),nullable=False,default='nuevo')
    notes=Column(Text,nullable=False,default='')
    created_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

class WorkspaceChannel(Base):
    __tablename__='workspace_channels'
    __table_args__=(UniqueConstraint('scope','provider',name='uq_workspace_channel'),)
    id=Column(Integer,primary_key=True)
    scope=Column(String(64),nullable=False,index=True)
    provider=Column(String(24),nullable=False)
    label=Column(String(120),nullable=False)
    encrypted_credentials=Column(Text,nullable=False)
    connected_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)
    updated_at=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
