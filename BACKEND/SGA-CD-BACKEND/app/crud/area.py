from sqlalchemy.orm import Session
from typing import List

from app.models.area import Area
from app.schemas.area import AreaCreate, AreaUpdate

def get_areas_by_tenant(db: Session, *, inquilino_id: int, skip: int = 0, limit: int = 100) -> List[Area]:
    """
    Retrieve all areas for a specific tenant.
    """
    return (
        db.query(Area)
        .filter(Area.inquilino_id == inquilino_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_area(db: Session, *, obj_in: AreaCreate, inquilino_id: int) -> Area:
    """
    Create a new area for a tenant.
    """
    db_obj = Area(**obj_in.dict(), inquilino_id=inquilino_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
