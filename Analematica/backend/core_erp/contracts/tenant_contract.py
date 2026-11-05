from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class TenantDTO:
    """
    Data Transfer Object para información básica de un Tenant.
    """
    id: UUID
    name: str
    is_active: bool
    plan_id: Optional[UUID] = None

class TenantContract:
    """
    Interfaz para la gestión de Tenants sin acoplamiento a modelos.
    """
    pass
