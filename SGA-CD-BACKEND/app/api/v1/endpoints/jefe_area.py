from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, crud
from app.models import user as user_model
from app.api import deps

router = APIRouter()

@router.get("/staff", response_model=List[schemas.user.User], summary="List all staff for the current Jefe de Área")
def get_my_staff(
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["jefe_area"]))
):
    """
    Get all staff members assigned to the same areas as the currently logged-in jefe_area.
    (Protected: jefe_area only)
    """
    staff = crud.jefe_area.get_staff_by_jefe_area(db=db, jefe_area=current_user)
    return staff


@router.get("/events", response_model=List[schemas.evento.Evento], summary="List all events for the current Jefe de Área's areas")
def get_my_area_events(
    db: Session = Depends(deps.get_db),
    current_user: user_model.Usuario = Depends(deps.role_required(["jefe_area"]))
):
    """
    Get all events in the areas managed by the currently logged-in jefe_area.
    (Protected: jefe_area only)
    """
    if not current_user.areas:
        return [] # Return empty list if the jefe is not assigned to any area

    area_ids = [area.id for area in current_user.areas]
    events = crud.evento.get_eventos_by_area_ids(db=db, area_ids=area_ids)
    return events
