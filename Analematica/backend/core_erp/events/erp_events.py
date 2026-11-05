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
class ErpImpactRequested(DomainEvent):
    event_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[int] = None
