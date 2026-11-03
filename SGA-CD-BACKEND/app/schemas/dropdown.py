from pydantic import BaseModel
from typing import Optional

# Base schema with the common field 'nombre'
class DropdownBase(BaseModel):
    nombre: str

# Schema for creating a new dropdown item
class DropdownCreate(DropdownBase):
    inquilino_id: int

# Schema for updating a dropdown item
class DropdownUpdate(DropdownBase):
    pass

# Base schema for items stored in the DB
class DropdownInDBBase(DropdownBase):
    id: int
    inquilino_id: int

    class Config:
        from_attributes = True

# Schema for returning a dropdown item to the client
class Dropdown(DropdownInDBBase):
    pass
