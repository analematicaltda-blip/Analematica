from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text
)
from sqlalchemy.orm import relationship
from .base import Base

class Elemento(Base):
    __tablename__ = "elementos"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    codigo = Column(String, nullable=False, index=True)
    descripcion = Column(Text)
    area = Column(String)
    nombre = Column(String, nullable=True)
    categoria = Column(String, nullable=True)
    foto_url = Column(String, nullable=True)
    fecha_alta = Column(DateTime(timezone=True), nullable=True)
    vida_util_anos = Column(Integer, default=5)
    estado_fisico = Column(String, default="Nuevo")  # Nuevo, Bueno, En Reparacion, Dado de Baja

class Prestamo(Base):
    __tablename__ = "prestamos"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    elemento_id = Column(Integer, ForeignKey("elementos.id"))
    instructor_id = Column(Integer, ForeignKey("profesores.id"))
    almacenista_id = Column(Integer, ForeignKey("almacenistas.id"))
    fecha_prestamo = Column(DateTime(timezone=True))
    observaciones_prestamo = Column(Text)
    foto_prestamo = Column(String)
    estado = Column(String)
    fecha_entrega = Column(DateTime(timezone=True))
    observaciones_entrega = Column(Text)
    foto_entrega = Column(String)
    estado_entrega = Column(String)
    area = Column(String)

    elemento = relationship("Elemento")
    # Note: relationships to Profesor and Almacenista are tricky if they are in another file.
    # We will need to use string-based relationship definitions.
    instructor = relationship("Profesor")
    almacenista = relationship("Almacenista")
