from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

@dataclass
class DomainEvent:
    event_id: uuid.UUID = field(default_factory=uuid.uuid4)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AccountingEvent(DomainEvent):
    """Base class for accounting-related events."""
    tenant_id: str = ""

@dataclass
class ReservationConfirmed(AccountingEvent):
    total_amount: float = 0.0
    commission_rate: float = 0.10
    reference: str = ""

@dataclass
class PaymentReceived(AccountingEvent):
    amount: float = 0.0
    reference: str = ""

@dataclass
class ProviderPaid(AccountingEvent):
    amount: float = 0.0
    reference: str = ""

@dataclass
class ReservationCancelled(AccountingEvent):
    original_journal_id: str = ""

@dataclass
class FinancialPosted(AccountingEvent):
    entry_id: str = ""
    total_amount: float = 0.0

@dataclass
class FinancialDiscrepancyDetected(AccountingEvent):
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
