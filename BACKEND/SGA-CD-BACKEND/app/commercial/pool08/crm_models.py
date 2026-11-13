"""Additive metadata and audit; WorkspaceLead remains the SGA contact identity."""
from sqlalchemy import Column,String,Integer,JSON,UniqueConstraint
from app.models.base import Base
class CRMContact(Base):
    __tablename__='sga_commercial_crm_contact'
    id=Column(String(96),primary_key=True)
    scope=Column(String(96),nullable=False,index=True)
    revision=Column(Integer,nullable=False)
    document=Column(JSON,nullable=False)
    base_fingerprint=Column(String(64),nullable=False)
class CRMEvent(Base):
    __tablename__='sga_commercial_crm_event'
    sequence=Column(Integer,primary_key=True,autoincrement=True)
    id=Column(String(36),nullable=False,unique=True)
    scope=Column(String(96),nullable=False,index=True)
    contact=Column(String(96),nullable=False,index=True)
    document=Column(JSON,nullable=False)
