from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Evento Schemas ---

class EventoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    tipo: str # 'evento' o 'salida'
    alcance: str # 'nacional', 'regional', 'internacional'
    area: str # 'Cultura', 'Deportes'
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    lugar: Optional[str] = None

class EventoCreate(EventoBase):
    inquilino_id: int
    creado_por_usuario_id: int

class EventoUpdate(EventoBase):
    pass

class EventoInDBBase(EventoBase):
    id: int
    inquilino_id: int
    creado_por_usuario_id: int
    class Config:
        from_attributes = True

class Evento(EventoInDBBase):
    pass


# --- EventoParticipante Schemas ---

class EventoParticipanteBase(BaseModel):
    evento_id: int
    usuario_id: int
    rol_participacion: Optional[str] = None

class EventoParticipanteCreate(EventoParticipanteBase):
    inquilino_id: int

class EventoParticipanteInDBBase(EventoParticipanteBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class EventoParticipante(EventoParticipanteInDBBase):
    pass
