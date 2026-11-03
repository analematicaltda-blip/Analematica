from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Inscripcion Schemas ---

class InscripcionBase(BaseModel):
    alumno_id: int
    clase_id: int
    nivel_formacion: Optional[str] = None
    area: str

class InscripcionCreate(InscripcionBase):
    inquilino_id: int
    fecha_inscripcion: datetime

class InscripcionInDBBase(InscripcionBase):
    id: int
    inquilino_id: int
    fecha_inscripcion: datetime
    class Config:
        from_attributes = True

class Inscripcion(InscripcionInDBBase):
    pass


# --- Asistencia Schemas ---

class AsistenciaBase(BaseModel):
    alumno_id: int
    clase_id: int
    evidencia_path: Optional[str] = None

class AsistenciaCreate(AsistenciaBase):
    inquilino_id: int
    fecha_hora: datetime

class AsistenciaInDBBase(AsistenciaBase):
    id: int
    inquilino_id: int
    fecha_hora: datetime
    class Config:
        from_attributes = True

class Asistencia(AsistenciaInDBBase):
    pass
