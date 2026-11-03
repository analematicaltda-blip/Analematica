from sqlalchemy import (
    Column, Integer, String, ForeignKey
)
from .base import Base

def create_dropdown_model(table_name):
    """
    A factory function to create simple dropdown models to avoid code repetition.
    Each model will have an id, a tenant id, and a name.
    """
    class DropdownModel(Base):
        __tablename__ = table_name
        id = Column(Integer, primary_key=True, index=True)
        inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
        nombre = Column(String, nullable=False)

    # Dynamically set the class name for better representation
    class_name = ''.join(word.capitalize() for word in table_name.split('_'))
    DropdownModel.__name__ = class_name

    return DropdownModel

# Create all the dropdown table models using the factory
Genero = create_dropdown_model("generos")
GrupoEtario = create_dropdown_model("grupos_etarios")
TipoDocumento = create_dropdown_model("tipos_documento")
Escolaridad = create_dropdown_model("escolaridades")
Discapacidad = create_dropdown_model("discapacidades")
GrupoPoblacional = create_dropdown_model("grupos_poblacionales")
Barrio = create_dropdown_model("barrios")
Vereda = create_dropdown_model("veredas")
Resguardo = create_dropdown_model("resguardos")
TipoEscenario = create_dropdown_model("tipos_escenario")
