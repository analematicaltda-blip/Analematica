from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class CatalogoEspecialidad(Base):
    __tablename__ = "catalogo_especialidades"

    id = Column(Integer, primary_key=True, index=True)
    vertical = Column(String(20), nullable=False)  # 'deporte' | 'cultura'
    categoria = Column(String(100), nullable=False)
    codigo_canonico = Column(String(150), nullable=False)
    nombre = Column(String(200), nullable=False)
    es_estandar = Column(Boolean, default=True)
    creado_por_inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())

    creador_inquilino = relationship("Inquilino")

    __table_args__ = (
        Index("uq_especialidad_clean", vertical, func.lower(func.trim(nombre)), unique=True),
    )


class EmpresaEspecialidad(Base):
    __tablename__ = "empresa_especialidades"

    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    especialidad_id = Column(Integer, ForeignKey("catalogo_especialidades.id"), nullable=False)
    activa = Column(Boolean, default=True)
    fecha_adopcion = Column(DateTime(timezone=True), server_default=func.now())

    inquilino = relationship("Inquilino")
    especialidad = relationship("CatalogoEspecialidad")

    __table_args__ = (
        UniqueConstraint("inquilino_id", "especialidad_id", name="uq_empresa_especialidad"),
    )


class ProfesorEspecialidad(Base):
    __tablename__ = "profesor_especialidades"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    empresa_especialidad_id = Column(Integer, ForeignKey("empresa_especialidades.id"), nullable=False)
    certificacion_avalada = Column(Boolean, default=False)
    nivel_academico = Column(String(100), nullable=True)

    usuario = relationship("Usuario")
    empresa_especialidad = relationship("EmpresaEspecialidad")
