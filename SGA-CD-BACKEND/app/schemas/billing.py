from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

# --- PaymentGateway Schemas ---
class PaymentGatewayBase(BaseModel):
    gateway_name: str
    is_active: bool = True

class PaymentGatewayCreate(PaymentGatewayBase):
    pass

class PaymentGateway(PaymentGatewayBase):
    id: int
    class Config:
        from_attributes = True


# --- SubscriptionPlan Schemas ---
class SubscriptionPlanBase(BaseModel):
    name: str
    price: float
    currency: str
    features: Optional[str] = None

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlan(SubscriptionPlanBase):
    id: int
    class Config:
        from_attributes = True


# --- Subscription Schemas ---
class SubscriptionBase(BaseModel):
    plan_id: int
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    generic_customer_id: Optional[str] = None

class SubscriptionCreate(SubscriptionBase):
    inquilino_id: int

class SubscriptionUpdate(BaseModel):
    plan_id: Optional[int] = None
    status: Optional[str] = None
    end_date: Optional[datetime] = None

class Subscription(SubscriptionBase):
    id: int
    inquilino_id: int
    plan: SubscriptionPlan
    class Config:
        from_attributes = True


# --- Payment Schemas ---
class PaymentBase(BaseModel):
    amount: float
    currency: str
    status: str
    gateway_name: str
    gateway_transaction_id: Optional[str] = None

class PaymentCreate(PaymentBase):
    subscription_id: int
    inquilino_id: int

class Payment(PaymentBase):
    id: int
    subscription_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# --- Schemas for Payment Intent ---
class PaymentIntentCreate(BaseModel):
    amount: float
    currency: str = "USD"

class PaymentIntent(BaseModel):
    client_secret: str


# --- MercadoPago Schemas ---
class MercadoPagoPreference(BaseModel):
    redirect_url: str


# --- Wompi Schemas ---
class WompiTransaction(BaseModel):
    redirect_url: str