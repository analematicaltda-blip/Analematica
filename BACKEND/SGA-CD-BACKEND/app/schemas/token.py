from pydantic import BaseModel
from typing import List

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    sub: int | None = None
    roles: List[str] = []
    inquilino_id: int | None = None
