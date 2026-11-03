from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# --- GamificacionAccion Schemas ---

class GamificacionAccionBase(BaseModel):
    accion_key: str
    puntos: int

class GamificacionAccionCreate(GamificacionAccionBase):
    inquilino_id: int

class GamificacionAccionUpdate(GamificacionAccionBase):
    pass

class GamificacionAccionInDBBase(GamificacionAccionBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class GamificacionAccion(GamificacionAccionInDBBase):
    pass


# --- GamificacionPuntosLog Schemas ---

class GamificacionPuntosLogBase(BaseModel):
    alumno_id: int
    accion_key: str
    puntos_ganados: int
    timestamp: datetime

class GamificacionPuntosLogCreate(GamificacionPuntosLogBase):
    inquilino_id: int

# No update schema for logs, as they are typically immutable
# No full 'GamificacionPuntosLog' schema needed if we only create and read lists

class GamificacionPuntosLogInDBBase(GamificacionPuntosLogBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class GamificacionPuntosLog(GamificacionPuntosLogInDBBase):
    pass


# --- GamificacionMedalla Schemas ---

class GamificacionMedallaBase(BaseModel):
    medalla_key: str
    nombre: str
    descripcion: Optional[str] = None
    icono_path: Optional[str] = None
    es_manual: bool = False

class GamificacionMedallaCreate(GamificacionMedallaBase):
    inquilino_id: int

class GamificacionMedallaUpdate(GamificacionMedallaBase):
    pass

class GamificacionMedallaInDBBase(GamificacionMedallaBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class GamificacionMedalla(GamificacionMedallaInDBBase):
    pass


# --- GamificacionMedallaObtenida Schemas ---

class GamificacionMedallaObtenidaBase(BaseModel):
    alumno_id: int
    medalla_key: str
    fecha_obtencion: datetime

class GamificacionMedallaObtenidaCreate(GamificacionMedallaObtenidaBase):
    inquilino_id: int

class GamificacionMedallaObtenidaInDBBase(GamificacionMedallaObtenidaBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class GamificacionMedallaObtenida(GamificacionMedallaObtenidaInDBBase):
    pass


# --- GamificacionMision Schemas ---

class GamificacionMisionBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    puntos_recompensa: int = 0
    medalla_recompensa_key: Optional[str] = None
    es_grupal: bool = False
    fecha_limite: Optional[datetime] = None

class GamificacionMisionCreate(GamificacionMisionBase):
    inquilino_id: int

class GamificacionMisionUpdate(GamificacionMisionBase):
    pass

class GamificacionMisionInDBBase(GamificacionMisionBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class GamificacionMision(GamificacionMisionInDBBase):
    pass


# --- GamificacionMercadoItem Schemas ---

class GamificacionMercadoItemBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    costo_puntos: int
    stock: int = -1
    tipo: str = "virtual"

class GamificacionMercadoItemCreate(GamificacionMercadoItemBase):
    inquilino_id: int

class GamificacionMercadoItemUpdate(GamificacionMercadoItemBase):
    pass

class GamificacionMercadoItemInDBBase(GamificacionMercadoItemBase):
    id: int
    inquilino_id: int
    class Config:
        from_attributes = True

class GamificacionMercadoItem(GamificacionMercadoItemInDBBase):
    pass
