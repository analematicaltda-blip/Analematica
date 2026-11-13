"""Owned opportunity state and append-only API audit records."""
from sqlalchemy import Column,String,Integer,JSON
from app.models.base import Base
class CommercialPrice(Base):
    __tablename__='sga_commercial_price'
    id=Column(String(36),primary_key=True)
    scope=Column(String(96),nullable=False,index=True)
    code=Column(String(40),nullable=False,index=True)
    revision=Column(Integer,nullable=False)
    status=Column(String(20),nullable=False,index=True)
    document=Column(JSON,nullable=False)
    document_digest=Column(String(64),nullable=False)
class PriceEvent(Base):
    __tablename__='sga_commercial_price_event'
    sequence=Column(Integer,primary_key=True,autoincrement=True)
    id=Column(String(36),nullable=False,unique=True)
    scope=Column(String(96),nullable=False,index=True)
    item_id=Column(String(36),nullable=True,index=True)
    document=Column(JSON,nullable=False)
