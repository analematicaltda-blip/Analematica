from sqlalchemy.orm import Session
from typing import List

from app.models.user import Usuario
from app.models.area import Area

def get_staff_by_jefe_area(db: Session, *, jefe_area: Usuario) -> List[Usuario]:
    """
    Retrieves all staff members (coordinadores, profesores, etc.)
    who belong to the same areas as the given jefe_area.
    """
    if not jefe_area.areas:
        # If the jefe_area is not assigned to any area, they have no staff.
        return []

    # Get the IDs of the areas managed by the jefe_area
    area_ids = [area.id for area in jefe_area.areas]

    # Define the roles that are considered 'staff' under a jefe_area
    staff_roles = ["coordinador", "profesor", "tecnico_area", "profesional_area"]

    # Find all users who are in the same areas and have one of the staff roles.
    # Exclude the jefe_area themselves from the results.
    staff_members = (
        db.query(Usuario)
        .join(Usuario.areas)
        .filter(Area.id.in_(area_ids))
        .filter(Usuario.rol.in_(staff_roles))
        .filter(Usuario.id != jefe_area.id)
        .distinct()
        .all()
    )

    return staff_members
