from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid
from datetime import datetime, timezone

class InputModality(str, Enum):
    TEXT = "TEXT"
    VOICE_TRANSCRIPT = "VOICE_TRANSCRIPT"
    VOICE_STREAM = "VOICE_STREAM"

class InteractionPriority(str, Enum):
    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EMERGENCY = "EMERGENCY"

class NekoContextBuffer(BaseModel):
    session_id: str = Field(..., description="ID de la sesion activa")
    user_id: str = Field(..., description="ID del usuario emisor")
    tenant_id: str = Field(..., description="ID del inquilino verificado")
    device_tier: int = Field(default=0, ge=0, le=2)
    recent_dialog_turns: List[Dict[str, str]] = Field(default_factory=list)

class MissionDispatchEnvelope(BaseModel):
    """CONTRATO DE SALIDA DE N.E.K.O. HACIA JARVI"""
    model_config = ConfigDict(frozen=True)

    contract_version: str = Field(default="1.0.0")
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    origin_user_id: str = Field(...)
    origin_tenant_id: str = Field(...)
    user_roles: List[str] = Field(...)
    raw_utterance: str = Field(...)
    modality: InputModality = Field(default=InputModality.TEXT)
    target_division: str = Field(..., description="DEPORTES, CULTURA, VENTAS, MARKETING, MULTIMEDIA")
    intent_action: str = Field(...)
    extracted_parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    priority: InteractionPriority = Field(default=InteractionPriority.NORMAL)