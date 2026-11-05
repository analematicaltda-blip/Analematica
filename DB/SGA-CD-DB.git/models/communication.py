from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text, Boolean
)
from sqlalchemy.orm import relationship
from .base import Base

class ChatConversacion(Base):
    __tablename__ = "chat_conversaciones"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), nullable=False)
    ultimo_mensaje_timestamp = Column(DateTime(timezone=True))

class ChatParticipante(Base):
    __tablename__ = "chat_participantes"
    id = Column(Integer, primary_key=True, index=True)
    conversacion_id = Column(Integer, ForeignKey("chat_conversaciones.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

class ChatMensaje(Base):
    __tablename__ = "chat_mensajes"
    id = Column(Integer, primary_key=True, index=True)
    conversacion_id = Column(Integer, ForeignKey("chat_conversaciones.id"), nullable=False)
    remitente_usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    leido = Column(Boolean, default=False)

    remitente = relationship("Usuario")

class ForoClase(Base):
    __tablename__ = "foros_clases"
    id = Column(Integer, primary_key=True, index=True)
    clase_id = Column(Integer, ForeignKey("clases.id"), unique=True, nullable=False)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    nombre_foro = Column(String, nullable=False)

    clase = relationship("Clase")

class ForoHilo(Base):
    __tablename__ = "foros_hilos"
    id = Column(Integer, primary_key=True, index=True)
    foro_id = Column(Integer, ForeignKey("foros_clases.id"), nullable=False)
    titulo = Column(String, nullable=False)
    creado_por_usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)

    foro = relationship("ForoClase")
    creador = relationship("Usuario")

class ForoPublicacion(Base):
    __tablename__ = "foros_publicaciones"
    id = Column(Integer, primary_key=True, index=True)
    hilo_id = Column(Integer, ForeignKey("foros_hilos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    contenido = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    responde_a_id = Column(Integer, ForeignKey("foros_publicaciones.id"))

    hilo = relationship("ForoHilo")
    autor = relationship("Usuario")
    parent_post = relationship("ForoPublicacion", remote_side=[id])
