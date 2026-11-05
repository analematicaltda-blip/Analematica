from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Float, Boolean
)
from sqlalchemy.orm import relationship
from .base import Base

class PaymentGateway(Base):
    __tablename__ = "payment_gateways"
    id = Column(Integer, primary_key=True, index=True)
    gateway_name = Column(String, unique=True, nullable=False, index=True) # e.g., 'stripe', 'mercadopago'
    is_active = Column(Boolean, default=True)
    # Aquí se podrían guardar configuraciones específicas si fuera necesario, en un campo JSON

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    features = Column(String) # Simple comma-separated list or JSON

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), unique=True, nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    status = Column(String, nullable=False) # 'trial', 'active', 'past_due', 'canceled'

    # ID de cliente agnóstico a la pasarela, puede ser usado por varias
    generic_customer_id = Column(String, index=True)

    inquilino = relationship("Inquilino")
    plan = relationship("SubscriptionPlan")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, nullable=False, default="USD")
    status = Column(String, nullable=False, index=True) # 'pending', 'succeeded', 'failed'

    # Campos agnósticos de la pasarela
    gateway_name = Column(String, ForeignKey("payment_gateways.gateway_name"), nullable=False)
    gateway_transaction_id = Column(String, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)

    subscription = relationship("Subscription")
    gateway = relationship("PaymentGateway")
