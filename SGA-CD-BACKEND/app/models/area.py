from sqlalchemy import Column, Integer, String, ForeignKey, Table
from .base import Base

# This is the association table for the many-to-many relationship
# between users and areas. It does not need its own model class.
usuario_areas_association = Table(
    "usuario_areas",
    Base.metadata,
    Column("usuario_id", Integer, ForeignKey("usuarios.id"), primary_key=True),
    Column("area_id", Integer, ForeignKey("areas.id"), primary_key=True),
)

class Area(Base):
    """
    Model for the main areas of the organization, e.g., 'Cultura', 'Deportes'.
    """
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, nullable=False, index=True)
