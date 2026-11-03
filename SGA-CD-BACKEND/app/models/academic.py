from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text, Boolean
)
from sqlalchemy.orm import relationship
from .base import Base

class ProcesoFormacion(Base):
    __tablename__ = "procesos_formacion"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    nombre_proceso = Column(String, nullable=False)
    tipo_proceso = Column(String)
    descripcion = Column(Text)
    inquilino = relationship("Inquilino")

class Escenario(Base):
    __tablename__ = "escenarios"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    ubicacion = Column(String)
    capacidad = Column(Integer)
    tipo = Column(String)
    area = Column(String) # 'Cultura', 'Deportes'
    inquilino = relationship("Inquilino")
    partes = relationship("EscenarioParte", back_populates="escenario", cascade="all, delete-orphan")

class EscenarioParte(Base):
    __tablename__ = "escenario_partes"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    escenario_id = Column(Integer, ForeignKey("escenarios.id"), nullable=False)
    nombre_parte = Column(String, nullable=False)
    descripcion = Column(Text)
    capacidad = Column(Integer)
    area = Column(String)
    escenario = relationship("Escenario", back_populates="partes")

class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    escenario_parte_id = Column(Integer, ForeignKey("escenario_partes.id"), nullable=False)
    usuario_id_reserva = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    proposito = Column(String)
    descripcion_proposito = Column(Text)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_fin = Column(DateTime(timezone=True), nullable=False)
    estado = Column(String, default="Confirmada")
    area = Column(String)
    escenario_parte = relationship("EscenarioParte")
    usuario_reserva = relationship("Usuario")

class Clase(Base):
    __tablename__ = "clases"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    nombre_clase = Column(String)
    proceso_id = Column(Integer, ForeignKey("procesos_formacion.id"))
    instructor_id = Column(Integer, ForeignKey("profesores.id"))
    fecha = Column(DateTime(timezone=True))
    hora_inicio = Column(String)
    hora_fin = Column(String)
    escenario_id = Column(Integer, ForeignKey("escenarios.id"))
    espacio = Column(String)
    grupo = Column(String)
    novedad = Column(Text)
    area = Column(String, nullable=False)
    proceso = relationship("ProcesoFormacion")
    instructor = relationship("Profesor")
    escenario = relationship("Escenario")

class Inscripcion(Base):
    __tablename__ = "inscripciones"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"))
    clase_id = Column(Integer, ForeignKey("clases.id"))
    fecha_inscripcion = Column(DateTime(timezone=True))
    nivel_formacion = Column(String)
    area = Column(String, nullable=False)
    alumno = relationship("Alumno")
    clase = relationship("Clase")

class Asistencia(Base):
    __tablename__ = "asistencias"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"))
    clase_id = Column(Integer, ForeignKey("clases.id"))
    fecha_hora = Column(DateTime(timezone=True))
    evidencia_path = Column(String)
    alumno = relationship("Alumno")
    clase = relationship("Clase")

class Evento(Base):
    __tablename__ = "eventos"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    tipo = Column(String, nullable=False) # 'evento', 'salida'
    alcance = Column(String, nullable=False) # 'nacional', 'regional', 'internacional'
    area = Column(String, nullable=False) # 'Cultura', 'Deportes'
    fecha_inicio = Column(DateTime(timezone=True))
    fecha_fin = Column(DateTime(timezone=True))
    lugar = Column(String)
    creado_por_usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    creador = relationship("Usuario")

class EventoParticipante(Base):
    __tablename__ = "evento_participantes"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    rol_participacion = Column(String)
    evento = relationship("Evento")
    participante = relationship("Usuario")

class Notificacion(Base):
    __tablename__ = "notificaciones"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    mensaje = Column(Text)
    fecha_hora = Column(DateTime(timezone=True))
    leido = Column(Boolean, default=False)
    usuario = relationship("Usuario")

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    usuario_id_actor = Column(Integer, ForeignKey("usuarios.id"))
    accion = Column(String, nullable=False)
    detalles = Column(Text) # JSON string
    timestamp = Column(DateTime(timezone=True), nullable=False)
    actor = relationship("Usuario")
