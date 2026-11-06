from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
from sqlalchemy.sql import func
from .base import Base

class Inquilino(Base):
    __tablename__ = "inquilinos"

    id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String, nullable=False)
    fecha_suscripcion = Column(DateTime(timezone=True), server_default=func.now())
    plan = Column(String)  # e.g., 'gratis', 'mensual', 'anual'
    api_key = Column(String, unique=True, index=True)
    activo = Column(Boolean, default=True)

    # --- LLM Configuration ---
    llm_preference = Column(String, default='local') # e.g., 'local', 'openai', 'google'
    openai_api_key = Column(String)
    google_api_key = Column(String)

    # --- Classification B2B (Naturaleza x Ámbito - 12 Combinaciones) ---
    tipo_organizacion = Column(String, default="entidad_publica") # entidad_publica, entidad_privada, empresa_publica, empresa_privada
    ambito_organizacional = Column(String, default="municipal")    # nacional, departamental, municipal
    vocacion_institucional = Column(String(20), nullable=False, default="deportiva", server_default="deportiva") # deportiva | cultural

    # Location columns
    direccion = Column(String)
    municipio = Column(String)
    pais = Column(String)
    latitud = Column(Float)
    longitud = Column(Float)
