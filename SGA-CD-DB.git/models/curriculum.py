from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text
)
from sqlalchemy.orm import relationship
from .base import Base

class PlanCurricular(Base):
    __tablename__ = "plan_curricular"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    nombre_plan = Column(String, nullable=False)
    descripcion = Column(Text)
    creado_por_usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    proceso_id = Column(Integer, ForeignKey("procesos_formacion.id"))
    area = Column(String, nullable=False)

    creador = relationship("Usuario")
    proceso = relationship("ProcesoFormacion")
    temas = relationship("PlanCurricularTema", back_populates="plan", cascade="all, delete-orphan")

class PlanCurricularTema(Base):
    __tablename__ = "plan_curricular_temas"
    id = Column(Integer, primary_key=True, index=True)
    plan_curricular_id = Column(Integer, ForeignKey("plan_curricular.id"), nullable=False)
    nombre_tema = Column(String, nullable=False)
    descripcion_tema = Column(Text)
    orden = Column(Integer, nullable=False)

    plan = relationship("PlanCurricular", back_populates="temas")

class PlanificadorClasesEventos(Base):
    __tablename__ = "planificador_clases_eventos"
    id = Column(Integer, primary_key=True, index=True)
    tema_id = Column(Integer, ForeignKey("plan_curricular_temas.id"), nullable=False)
    instructor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    clase_id = Column(Integer, ForeignKey("clases.id"))
    fecha_programada = Column(DateTime(timezone=True), nullable=False)
    estado = Column(String, nullable=False) # 'planificado', 'completado', etc.

    tema = relationship("PlanCurricularTema")
    instructor = relationship("Usuario")
    clase = relationship("Clase")

class ProgresoAlumnoTema(Base):
    __tablename__ = "progreso_alumno_tema"
    id = Column(Integer, primary_key=True, index=True)
    alumno_usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tema_id = Column(Integer, ForeignKey("plan_curricular_temas.id"), nullable=False)
    estado = Column(String, nullable=False)
    fecha_completado = Column(DateTime(timezone=True))
    observaciones = Column(Text)
    evaluacion = Column(Text)

    alumno = relationship("Usuario")
    tema = relationship("PlanCurricularTema")

class ContenidoCurricular(Base):
    __tablename__ = "contenido_curricular"
    id = Column(Integer, primary_key=True, index=True)
    tema_id = Column(Integer, ForeignKey("plan_curricular_temas.id"), nullable=False)
    tipo_contenido = Column(String, nullable=False) # 'pdf', 'video', 'enlace'
    titulo = Column(String, nullable=False)
    ruta_archivo_o_url = Column(String, nullable=False)
    subido_por_usuario_id = Column(Integer, ForeignKey("usuarios.id"))

    tema = relationship("PlanCurricularTema")
    uploader = relationship("Usuario")
