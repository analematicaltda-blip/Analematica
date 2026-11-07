from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# Shared properties for an Alumno
class AlumnoBase(BaseModel):
    tipo_documento: Optional[str] = None
    documento: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    grupo_etario: Optional[str] = None
    escolaridad: Optional[str] = None
    discapacidad: Optional[str] = None
    grupo_poblacional: Optional[str] = None
    barrio: Optional[str] = None
    vereda: Optional[str] = None
    resguardo: Optional[str] = None
    zona_geografica: Optional[str] = None
    telefono: Optional[str] = None
    mostrar_en_rankings: bool = True

# Properties to receive on item creation
class AlumnoCreate(AlumnoBase):
    # When creating an Alumno record, it must be linked to an existing Usuario
    usuario_id: int
    inquilino_id: int

# Properties to receive on item update
class AlumnoUpdate(AlumnoBase):
    pass

# Properties shared by models stored in DB
class AlumnoInDBBase(AlumnoBase):
    id: int
    usuario_id: int
    inquilino_id: int
    puntos_totales: int
    nivel: int

    class Config:
        from_attributes = True

# Properties to return to client
class Alumno(AlumnoInDBBase):
    pass

# Properties to return from DB
class AlumnoInDB(AlumnoInDBBase):
    pass


# --- Progreso del Alumno ---

class CalificacionReciente(BaseModel):
    materia: str
    nota: str

class LogroGamificacion(BaseModel):
    nombre: str

class AlumnoProgreso(BaseModel):
    asistencia_porcentaje: float
    asistencia_status: str
    calificaciones_recientes: List[CalificacionReciente]
    logros_gamificacion: List[LogroGamificacion]
