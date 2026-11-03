from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.billing import Suscripcion, Factura
from app.schemas.billing import SubscriptionCreate, SubscriptionUpdate, PaymentCreate

# --- SubscriptionPlan ---
# This seems to be missing from the Spanish model, commenting out for now.
# def get_plan_by_name(db: Session, name: str) -> Optional[SubscriptionPlan]:
#     return db.query(SubscriptionPlan).filter(SubscriptionPlan.name == name).first()

# --- Subscription ---
def get_subscription_by_tenant(db: Session, inquilino_id: int) -> Optional[Suscripcion]:
    return db.query(Suscripcion).filter(Suscripcion.inquilino_id == inquilino_id).first()

def create_subscription(db: Session, *, obj_in: SubscriptionCreate) -> Suscripcion:
    db_obj = Suscripcion(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_subscription(db: Session, *, db_obj: Suscripcion, obj_in: SubscriptionUpdate) -> Suscripcion:
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# --- Payment ---
def create_payment(db: Session, *, obj_in: PaymentCreate) -> Factura:
    from datetime import datetime, timezone
    data = obj_in.model_dump()
    monto = data.pop("amount", 0.0)
    status_val = data.pop("status", "pending")
    sub_id = data.pop("subscription_id", None)
    db_obj = Factura(
        suscripcion_id=sub_id,
        monto=monto,
        fecha_emision=datetime.now(timezone.utc),
        estado=status_val,
        **{k: v for k, v in data.items() if hasattr(Factura, k)}
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_payment_by_gateway_transaction_id(db: Session, transaction_id: str) -> Optional[Factura]:
    return db.query(Factura).filter(Factura.gateway_transaction_id == transaction_id).first()

def update_payment_status(db: Session, *, db_obj: Factura, status: str) -> Factura:
    db_obj.status = status
    db.commit()
    db.refresh(db_obj)
    return db_obj
