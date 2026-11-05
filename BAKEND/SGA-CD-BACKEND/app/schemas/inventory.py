from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- Elemento Schemas ---

class ElementoBase(BaseModel):
    codigo: str
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    area: Optional[str] = None
    foto_url: Optional[str] = None
    fecha_alta: Optional[datetime] = None
    vida_util_anos: Optional[int] = 5
    estado_fisico: Optional[str] = "Nuevo"

class ElementoCreate(ElementoBase):
    inquilino_id: int

class ElementoUpdate(ElementoBase):
    pass

class ElementoInDBBase(ElementoBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class Elemento(ElementoInDBBase):
    pass

# --- Prestamo Schemas ---

class PrestamoBase(BaseModel):
    elemento_id: int
    instructor_id: int
    almacenista_id: Optional[int] = None
    fecha_prestamo: datetime
    observaciones_prestamo: Optional[str] = None
    foto_prestamo: Optional[str] = None
    estado: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    observaciones_entrega: Optional[str] = None
    foto_entrega: Optional[str] = None
    estado_entrega: Optional[str] = None
    area: Optional[str] = None

class PrestamoCreate(PrestamoBase):
    inquilino_id: int

class PrestamoUpdate(PrestamoBase):
    pass

class PrestamoInDBBase(PrestamoBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class Prestamo(PrestamoInDBBase):
    pass
