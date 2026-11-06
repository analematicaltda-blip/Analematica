from pydantic import BaseModel

class AreaBase(BaseModel):
    nombre: str
    descripcion: str | None = None

class AreaCreate(AreaBase):
    pass

class AreaUpdate(AreaBase):
    pass

class Area(AreaBase):
    id: int
    inquilino_id: int

    class Config:
        orm_mode = True
