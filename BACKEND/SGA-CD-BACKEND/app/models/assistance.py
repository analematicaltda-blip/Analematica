"""Private guided sessions; no provider credentials, emails or screenshots are stored."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func, UniqueConstraint
from .base import Base

class AssistanceSession(Base):
    __tablename__ = 'assistance_sessions'
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False, index=True)
    workflow_id = Column(String(100), nullable=False)
    catalog_version = Column(String(40), nullable=False)
    workflow_snapshot = Column(Text, nullable=False)
    position = Column(Integer, nullable=False, default=0)
    revision = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default='active')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class AssistanceEvent(Base):
    __tablename__ = 'assistance_events'
    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), ForeignKey('assistance_sessions.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False)
    step_id = Column(String(100), nullable=False)
    event = Column(String(40), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class AssistanceAdvice(Base):
    __tablename__ = 'assistance_advice'
    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey('assistance_sessions.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False)
    source_revision = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)
    agent_id = Column(Integer)
    thread_id = Column(Integer)
    turn_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

class ControlPairing(Base):
    __tablename__ = 'assistance_control_pairings'
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False)
    code_hash = Column(String(64), nullable=False, unique=True)
    scopes = Column(Text, nullable=False)
    expires_at = Column(Integer, nullable=False)
    used = Column(Integer, nullable=False, default=0)

class ControlDevice(Base):
    __tablename__ = 'assistance_control_devices'
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False, index=True)
    name = Column(String(80), nullable=False)
    kind = Column(String(20), nullable=False, default='desktop')
    token_hash = Column(String(64), nullable=False, unique=True)
    scopes = Column(Text, nullable=False)
    revoked = Column(Integer, nullable=False, default=0)
    last_seen = Column(Integer, nullable=False, default=0)

class ControlJob(Base):
    __tablename__ = 'assistance_control_jobs'
    id = Column(String(36), primary_key=True)
    device_id = Column(String(36), ForeignKey('assistance_control_devices.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False, index=True)
    intent = Column(Text, nullable=False)  # encrypted canonical JSON
    digest = Column(String(64), nullable=False)
    required = Column(Integer, nullable=False)
    approvals = Column(Integer, nullable=False, default=0)
    status = Column(String(30), nullable=False, default='awaiting_review')
    challenge = Column(Text, nullable=False)  # encrypted, one stage only
    expires_at = Column(Integer, nullable=False)
    challenge_expires = Column(Integer, nullable=False)
    lease_id = Column(String(64))
    lease_expires = Column(Integer)
    result = Column(Text)
    stop_requested = Column(Integer, nullable=False, default=0)

class ControlApproval(Base):
    __tablename__ = 'assistance_control_approvals'
    __table_args__ = (UniqueConstraint('job_id','stage',name='uq_control_job_stage'),)
    id = Column(Integer, primary_key=True)
    job_id = Column(String(36), ForeignKey('assistance_control_jobs.id'), nullable=False, index=True)
    stage = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False)
    digest = Column(String(64), nullable=False)
    created_at = Column(Integer, nullable=False)


class ContentDraft(Base):
    __tablename__ = 'assistance_content_drafts'
    id = Column(String(36), primary_key=True)
    user_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey('inquilinos.id'), nullable=False, index=True)
    content = Column(Text, nullable=False)
    digest = Column(String(64), nullable=False)
    source = Column(Text, nullable=False)
    revision = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default='draft')
    reviewed_at = Column(Integer)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
