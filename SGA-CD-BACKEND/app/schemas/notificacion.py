from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificacionBase(BaseModel):
    mensaje: str
    leido: bool = False

class NotificacionCreate(NotificacionBase):
    inquilino_id: int
    usuario_id: int
    fecha_hora: datetime

class NotificacionUpdate(BaseModel):
    leido: Optional[bool] = None

class NotificacionInDBBase(NotificacionBase):
    id: int
    inquilino_id: int
    usuario_id: int
    fecha_hora: datetime

    class Config:
        from_attributes = True

class Notificacion(NotificacionInDBBase):
    pass
