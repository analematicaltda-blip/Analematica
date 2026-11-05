from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid
from datetime import datetime, timezone

class MissionExecutionState(str, Enum):
    PLANNING = "PLANNING"
    DISPATCHED = "DISPATCHED"
    WAITING_FOR_HUMAN_APPROVAL = "WAITING_FOR_HUMAN_APPROVAL"
    EXECUTING = "EXECUTING"
    COMPLETED_SUCCESS = "COMPLETED_SUCCESS"
    COMPLETED_PARTIAL = "COMPLETED_PARTIAL"
    FAILED = "FAILED"

class SubTaskExecutionOrder(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    assigned_corps: str = Field(...)
    minimum_military_rank: str = Field(default="SARGENTO")
    target_tool: str = Field(...)
    parameters: Dict[str, Any] = Field(...)
    idempotency_key: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timeout_seconds: int = Field(default=30)

class MissionReportToNeko(BaseModel):
    """CONTRATO DE RETORNO DE JARVI HACIA N.E.K.O."""
    correlation_id: str = Field(...)
    tenant_id: str = Field(...)
    final_state: MissionExecutionState = Field(...)
    execution_summary: str = Field(...)
    artifacts_created: List[Dict[str, Any]] = Field(default_factory=list)
    pending_approvals: Optional[Dict[str, Any]] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TrajectoryAuditRecord(BaseModel):
    """CONTRATO DE TELEMETRIA DE JARVI HACIA SOUP"""
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: str = Field(...)
    tenant_id_hashed: str = Field(...)
    agent_id: str = Field(...)
    tool_invoked: str = Field(...)
    input_payload: Dict[str, Any] = Field(...)
    tool_output: Optional[Dict[str, Any]] = Field(default=None)
    http_status_code: int = Field(default=200)
    execution_time_ms: float = Field(default=0.0)
    error_traceback: Optional[str] = Field(default=None)