from dataclasses import dataclass
from typing import Dict, Any, Optional
import uuid

@dataclass
class DomainCommand:
    """Base class for all domain commands."""
    correlation_id: uuid.UUID = uuid.uuid4()
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class CreateReservationCommand(DomainCommand):
    provider_id: str = ""
    customer_id: str = ""
    service_id: str = ""
    start_date: str = ""
    end_date: str = ""
    total_amount: float = 0.0

@dataclass
class ConfirmReservationCommand(DomainCommand):
    reserva_id: str = ""

@dataclass
class ProcessPaymentCommand(DomainCommand):
    provider_id: str = ""
    order_id: str = ""
    amount: float = 0.0
    payment_method: str = "CASH"

class IApplicationService:
    """Base interface for all application services."""
    def execute(self, command: DomainCommand) -> Dict[str, Any]:
        raise NotImplementedError
