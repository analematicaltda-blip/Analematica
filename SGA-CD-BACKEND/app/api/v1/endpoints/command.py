from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from app.api import deps
from app import models
from app.agents.command_staff import JarviGeneralOrchestrator, NekoConversationalGeneral

router = APIRouter()

# Instancia singleton del Estado Mayor en memoria
_jarvi = JarviGeneralOrchestrator()
_neko = NekoConversationalGeneral(orchestrator=_jarvi)

class CommandRequest(BaseModel):
    command: str

class CommandResponse(BaseModel):
    reply: str
    target_division: str
    status: str

@router.post("/command", response_model=CommandResponse)
async def execute_agent_command(
    req: CommandRequest,
    current_user: models.Usuario = Depends(deps.get_current_active_user)
):
    """
    Endpoint seguro para transmitir ordenes de voz/texto al Estado Mayor (N.E.K.O. y JARVI).
    Extrae la identidad, rol e inquilino_id del token JWT verificado.
    """
    if not req.command.strip():
        raise HTTPException(status_code=400, detail="El comando no puede estar vacio.")

    reply = await _neko.handle_user_command(
        command_text=req.command,
        user_id=str(current_user.id),
        tenant_id=str(current_user.inquilino_id),
        roles=[current_user.rol]
    )

    return CommandResponse(
        reply=reply,
        target_division="ESTADO_MAYOR_MULTIDIVISIONAL",
        status="success"
    )