from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from datetime import datetime

@dataclass(frozen=True)
class ReservationDTO:
    """
    DTO para comunicación entre dominios sobre reservas operativas.
    """
    reservation_id: UUID
    tenant_id: UUID
    total_amount: Decimal
    currency: str
    status: str
    created_at: datetime

class OperationalContract:
    """
    Interfaz para dominios operativos.
    """
    pass
