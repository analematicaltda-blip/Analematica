from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Chat Schemas ---

class ChatConversacionBase(BaseModel):
    pass # Usually created implicitly

class ChatConversacionCreate(ChatConversacionBase):
    inquilino_id: int
    participante_ids: List[int]

class ChatConversacion(ChatConversacionBase):
    id: int
    inquilino_id: int
    fecha_creacion: datetime
    ultimo_mensaje_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True

class ChatMensajeBase(BaseModel):
    contenido: str

class ChatMensajeCreate(ChatMensajeBase):
    conversacion_id: int
    remitente_usuario_id: int

class ChatMensaje(ChatMensajeBase):
    id: int
    conversacion_id: int
    remitente_usuario_id: int
    timestamp: datetime
    leido: bool

    class Config:
        from_attributes = True

# --- Foro Schemas ---

class ForoClaseBase(BaseModel):
    nombre_foro: str

class ForoClaseCreate(ForoClaseBase):
    clase_id: int
    inquilino_id: int

class ForoClase(ForoClaseBase):
    id: int
    clase_id: int
    inquilino_id: int

    class Config:
        from_attributes = True

class ForoHiloBase(BaseModel):
    titulo: str

class ForoHiloCreate(ForoHiloBase):
    foro_id: int
    creado_por_usuario_id: int

class ForoHilo(ForoHiloBase):
    id: int
    foro_id: int
    creado_por_usuario_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class ForoPublicacionBase(BaseModel):
    contenido: str
    responde_a_id: Optional[int] = None

class ForoPublicacionCreate(ForoPublicacionBase):
    hilo_id: int
    usuario_id: int

class ForoPublicacion(ForoPublicacionBase):
    id: int
    hilo_id: int
    usuario_id: int
    timestamp: datetime

    class Config:
        from_attributes = True
