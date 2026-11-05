from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# --- PlanCurricular Schemas ---

from datetime import datetime

class PlanCurricularBase(BaseModel):
    nombre_plan: str
    descripcion: Optional[str] = None
    proceso_id: Optional[int] = None
    area: str
    estado_aprobacion: Optional[str] = "borrador"
    observaciones_revision: Optional[str] = None
    vobo_coordinador_id: Optional[int] = None
    fecha_vobo: Optional[datetime] = None
    ratificacion_jefe_id: Optional[int] = None
    fecha_ratificacion: Optional[datetime] = None
    version: Optional[int] = 1

class PlanCurricularCreate(PlanCurricularBase):
    inquilino_id: int
    creado_por_usuario_id: int

class PlanCurricularUpdate(PlanCurricularBase):
    pass

class PlanCurricularReviewAction(BaseModel):
    observaciones: Optional[str] = None

class PlanCurricularInDBBase(PlanCurricularBase):
    id: int
    inquilino_id: int
    creado_por_usuario_id: int
    class Config:
        from_attributes = True

class PlanCurricular(PlanCurricularInDBBase):
    pass


# --- PlanCurricularTema Schemas ---

class PlanCurricularTemaBase(BaseModel):
    nombre_tema: str
    descripcion_tema: Optional[str] = None
    orden: int

class PlanCurricularTemaCreate(PlanCurricularTemaBase):
    plan_curricular_id: int

class PlanCurricularTemaUpdate(PlanCurricularTemaBase):
    pass

class PlanCurricularTemaInDBBase(PlanCurricularTemaBase):
    id: int
    plan_curricular_id: int
    class Config:
        from_attributes = True

class PlanCurricularTema(PlanCurricularTemaInDBBase):
    pass
