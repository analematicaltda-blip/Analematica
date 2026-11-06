from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.models import user as user_model

router = APIRouter()

class TareaDocenteCreate(BaseModel):
    profesor_id: int
    descripcion: str
    fecha: str
    horario: str

class TareaDocenteResponse(BaseModel):
    id: int
    profesor_id: int
    descripcion: str
    fecha: str
    horario: str
    estado: str = "Asignada"

@router.post("/profesores/tareas", response_model=TareaDocenteResponse, summary="Assign extraordinary task to teacher")
def assign_teacher_task(
    tarea_in: TareaDocenteCreate,
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["admin_empresa", "jefe_area", "coordinador"]))
) -> Any:
    """
    Assign extraordinary task or commission to a teacher.
    (Protected: coordinador, jefe_area, admin_empresa)
    """
    profesor = db.query(user_model.Profesor).filter(
        user_model.Profesor.id == tarea_in.profesor_id,
        user_model.Profesor.inquilino_id == current_user.inquilino_id
    ).first()

    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profesor not found in current tenant."
        )

    return TareaDocenteResponse(
        id=1001,
        profesor_id=tarea_in.profesor_id,
        descripcion=tarea_in.descripcion,
        fecha=tarea_in.fecha,
        horario=tarea_in.horario,
        estado="Asignada"
    )
