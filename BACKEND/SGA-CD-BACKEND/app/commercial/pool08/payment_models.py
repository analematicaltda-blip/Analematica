"""Owned payment intention state and append-only audit records."""
from sqlalchemy import Column,String,Integer,JSON,Boolean,UniqueConstraint
from app.models.base import Base
class CommercialPayment(Base):
    __tablename__='sga_commercial_payment'
    __table_args__=(UniqueConstraint('scope','code',name='sga_payment_scope_code'),)
    id=Column(String(36),primary_key=True)
    scope=Column(String(96),nullable=False,index=True)
    code=Column(String(100),nullable=False,index=True)
    revision=Column(Integer,nullable=False)
    status=Column(String(20),nullable=False,index=True)
    document=Column(JSON,nullable=False)
    document_digest=Column(String(64),nullable=False)
class PaymentEvent(Base):
    __tablename__='sga_commercial_payment_event'
    sequence=Column(Integer,primary_key=True,autoincrement=True)
    id=Column(String(36),nullable=False,unique=True)
    scope=Column(String(96),nullable=False,index=True)
    item_id=Column(String(36),nullable=True,index=True)
    document=Column(JSON,nullable=False)

