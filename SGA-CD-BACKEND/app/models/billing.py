from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Float, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Suscripcion(Base):
    __tablename__ = "suscripciones"
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), unique=True, nullable=False)
    plan = Column(String, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), nullable=False)
    fecha_fin = Column(DateTime(timezone=True))
    estado = Column(String, nullable=False) # 'en_prueba', 'activa', 'cancelada', 'vencida'
    stripe_customer_id = Column(String, index=True)
    stripe_subscription_id = Column(String, unique=True, index=True)

    inquilino = relationship("Inquilino")

class Factura(Base):
    __tablename__ = "facturas"
    id = Column(Integer, primary_key=True, index=True)
    suscripcion_id = Column(Integer, ForeignKey("suscripciones.id"), nullable=False)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False)
    monto = Column(Float, nullable=False)
    fecha_emision = Column(DateTime(timezone=True), nullable=False)
    fecha_pago = Column(DateTime(timezone=True))
    estado = Column(String, nullable=False) # 'pendiente', 'pagada', 'fallida'
    stripe_invoice_id = Column(String, unique=True, index=True)
    pdf_url = Column(String)

    suscripcion = relationship("Suscripcion")
    inquilino = relationship("Inquilino")

class ConsumoInquilino(Base):
    __tablename__ = "consumo_inquilinos"
    __table_args__ = (
        UniqueConstraint("inquilino_id", "periodo", "capacidad", name="uq_consumo_inquilino_periodo_capacidad"),
    )
    id = Column(Integer, primary_key=True, index=True)
    inquilino_id = Column(Integer, ForeignKey("inquilinos.id"), nullable=False, index=True)
    periodo = Column(String, nullable=False, index=True) # Formato "YYYY-MM"
    capacidad = Column(String, nullable=False, index=True) # ej. "images", "carousels", "videos", "reels", "llm_prompts", "social_posts"
    cantidad_usada = Column(Integer, default=0, nullable=False)
    ultima_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    inquilino = relationship("Inquilino")
