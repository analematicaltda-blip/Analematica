from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Escenario Schemas ---

class EscenarioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    capacidad: Optional[int] = None
    tipo: Optional[str] = None
    area: Optional[str] = None

class EscenarioCreate(EscenarioBase):
    inquilino_id: int

class EscenarioUpdate(EscenarioBase):
    pass

class EscenarioInDBBase(EscenarioBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class Escenario(EscenarioInDBBase):
    # This can be expanded to include related data like 'partes'
    pass


# --- EscenarioParte Schemas ---

class EscenarioParteBase(BaseModel):
    nombre_parte: str
    descripcion: Optional[str] = None
    capacidad: Optional[int] = None
    area: Optional[str] = None

class EscenarioParteCreate(EscenarioParteBase):
    inquilino_id: int
    escenario_id: int

class EscenarioParteUpdate(EscenarioParteBase):
    pass

class EscenarioParteInDBBase(EscenarioParteBase):
    id: int
    escenario_id: int
    class Config:
        from_attributes = True

class EscenarioParte(EscenarioParteInDBBase):
    pass


# --- Reserva Schemas ---

class ReservaBase(BaseModel):
    escenario_parte_id: int
    proposito: Optional[str] = None
    descripcion_proposito: Optional[str] = None
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: Optional[str] = "Confirmada"
    area: Optional[str] = None

class ReservaCreate(ReservaBase):
    pass

class ReservaUpdate(BaseModel):
    # Only some fields might be updatable
    proposito: Optional[str] = None
    descripcion_proposito: Optional[str] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    estado: Optional[str] = None

class ReservaInDBBase(ReservaBase):
    id: int
    inquilino_id: int
    usuario_id_reserva: int
    class Config:
        from_attributes = True

class Reserva(ReservaInDBBase):
    pass
