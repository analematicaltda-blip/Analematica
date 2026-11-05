from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Boolean
)
from sqlalchemy.orm import relationship
from .base import Base

class GamificacionAccion(Base):
    __tablename__ = "gamificacion_acciones"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    accion_key = Column(String, nullable=False)
    puntos = Column(Integer, nullable=False)

class GamificacionPuntosLog(Base):
    __tablename__ = "gamificacion_puntos_log"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    accion_key = Column(String, nullable=False)
    puntos_ganados = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    alumno = relationship("Alumno")

class GamificacionMedalla(Base):
    __tablename__ = "gamificacion_medallas"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    medalla_key = Column(String, nullable=False, unique=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    icono_path = Column(String)
    es_manual = Column(Boolean, default=False)

class GamificacionMedallaObtenida(Base):
    __tablename__ = "gamificacion_medallas_obtenidas"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    medalla_key = Column(String, nullable=False, unique=True)
    fecha_obtencion = Column(DateTime(timezone=True), nullable=False)

    alumno = relationship("Alumno")


class GamificacionMision(Base):
    __tablename__ = "gamificacion_misiones"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    puntos_recompensa = Column(Integer, default=0)
    medalla_recompensa_key = Column(String, ForeignKey("gamificacion_medallas.medalla_key"))
    es_grupal = Column(Boolean, default=False)
    fecha_limite = Column(DateTime(timezone=True))


class GamificacionMisionProgreso(Base):
    __tablename__ = "gamificacion_misiones_progreso"
    id = Column(Integer, primary_key=True, index=True)
    mision_id = Column(Integer, ForeignKey("gamificacion_misiones.id"), nullable=False)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    completada = Column(Boolean, default=False)
    fecha_completada = Column(DateTime(timezone=True))

    mision = relationship("GamificacionMision")
    alumno = relationship("Alumno")


class GamificacionMercadoItem(Base):
    __tablename__ = "gamificacion_mercado_items"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    costo_puntos = Column(Integer, nullable=False)
    stock = Column(Integer, default=-1)  # -1 para stock infinito (ítems virtuales)
    tipo = Column(String, default="virtual") # virtual, real


class GamificacionCompraLog(Base):
    __tablename__ = "gamificacion_compras_log"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("gamificacion_mercado_items.id"), nullable=False)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    costo_en_puntos = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    item = relationship("GamificacionMercadoItem")
    alumno = relationship("Alumno")
