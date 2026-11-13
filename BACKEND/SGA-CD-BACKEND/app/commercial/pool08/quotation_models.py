"""Owned opportunity state and append-only API audit records."""
from sqlalchemy import Column,String,Integer,JSON,LargeBinary
from app.models.base import Base
class CommercialQuotation(Base):
    __tablename__='sga_commercial_quotation'
    id=Column(String(36),primary_key=True)
    scope=Column(String(96),nullable=False,index=True)
    code=Column(String(100),nullable=False,index=True)
    revision=Column(Integer,nullable=False)
    status=Column(String(20),nullable=False,index=True)
    document=Column(JSON,nullable=False)
    document_digest=Column(String(64),nullable=False)
class QuotationEvent(Base):
    __tablename__='sga_commercial_quotation_event'
    sequence=Column(Integer,primary_key=True,autoincrement=True)
    id=Column(String(36),nullable=False,unique=True)
    scope=Column(String(96),nullable=False,index=True)
    item_id=Column(String(36),nullable=True,index=True)
    document=Column(JSON,nullable=False)

class QuotationAsset(Base):
    __tablename__='sga_commercial_quotation_asset'
    id=Column(String(36),primary_key=True)
    scope=Column(String(96),nullable=False,index=True)
    creator_ref=Column(String(96),nullable=False)
    data=Column(LargeBinary,nullable=False)
    mime=Column(String(40),nullable=False)
    digest=Column(String(64),nullable=False)
    original_digest=Column(String(64),nullable=False)
