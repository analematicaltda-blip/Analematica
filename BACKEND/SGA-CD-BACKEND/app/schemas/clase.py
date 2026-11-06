from pydantic import BaseModel
from typing import Optional
from datetime import date, time

# --- ProcesoFormacion Schemas ---

class ProcesoFormacionBase(BaseModel):
    nombre_proceso: str
    tipo_proceso: Optional[str] = None
    descripcion: Optional[str] = None

class ProcesoFormacionCreate(ProcesoFormacionBase):
    inquilino_id: int

class ProcesoFormacionUpdate(ProcesoFormacionBase):
    pass

class ProcesoFormacionInDBBase(ProcesoFormacionBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class ProcesoFormacion(ProcesoFormacionInDBBase):
    pass


# --- Clase Schemas ---

class ClaseBase(BaseModel):
    nombre_clase: Optional[str] = None
    proceso_id: Optional[int] = None
    instructor_id: Optional[int] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[str] = None # Using str for HH:MM format
    hora_fin: Optional[str] = None
    escenario_id: Optional[int] = None
    espacio: Optional[str] = None
    grupo: Optional[str] = None
    novedad: Optional[str] = None
    area: str

class ClaseCreate(ClaseBase):
    inquilino_id: int

class ClaseUpdate(ClaseBase):
    pass

class ClaseInDBBase(ClaseBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class Clase(ClaseInDBBase):
    pass
