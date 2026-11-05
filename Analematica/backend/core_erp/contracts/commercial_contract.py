from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from typing import List, Optional

@dataclass(frozen=True)
class CommercialPlanDTO:
    id: UUID
    name: str
    price: Decimal
    currency: str
    features: List[str]

@dataclass(frozen=True)
class SubscriptionDTO:
    id: UUID
    tenant_id: UUID
    plan_id: UUID
    status: str
    mrr: Decimal

class CommercialContract:
    """
    Interfaz para operaciones comerciales.
    """
    pass
