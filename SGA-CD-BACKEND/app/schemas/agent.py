from pydantic import BaseModel
from typing import Optional

class AgentInput(BaseModel):
    thread_id: str
    prompt: str
    area: str # 'Cultura' o 'Deportes'

class AgentOutput(BaseModel):
    text: str
    image_url: Optional[str] = None
    is_ai_generated: bool = True
    disclaimer_ia: str = "Respuesta generada por Inteligencia Artificial SGA-CD. Requiere verificación humana."
