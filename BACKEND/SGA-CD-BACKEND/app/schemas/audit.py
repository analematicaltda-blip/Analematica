from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AuditLogBase(BaseModel):
    accion: str
    detalles: Optional[str] = None # JSON string

class AuditLogCreate(AuditLogBase):
    inquilino_id: int
    usuario_id_actor: Optional[int] = None
    timestamp: datetime

class AuditLogInDBBase(AuditLogBase):
    id: int
    inquilino_id: int
    usuario_id_actor: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class AuditLog(AuditLogInDBBase):
    pass
