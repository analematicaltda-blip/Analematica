"""Additive analytical dimensions and explicit enrollment status history; no legacy ALTER."""
from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,UniqueConstraint,Text
from sqlalchemy.sql import func
from .base import Base
from . import academic,catalog,user

class InstitutionalProcess(Base):
    __tablename__='institutional_process_specialties'
    __table_args__=(UniqueConstraint('tenant_id','process_id',name='uq_institutional_process'),)
    id=Column(Integer,primary_key=True)
    tenant_id=Column(Integer,ForeignKey('inquilinos.id'),nullable=False,index=True)
    process_id=Column(Integer,ForeignKey('procesos_formacion.id'),nullable=False)
    specialty_id=Column(Integer,ForeignKey('catalogo_especialidades.id'),nullable=False)
    recorded_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)

class EnrollmentEvent(Base):
    __tablename__='institutional_enrollment_events'
    id=Column(Integer,primary_key=True)
    tenant_id=Column(Integer,ForeignKey('inquilinos.id'),nullable=False,index=True)
    enrollment_id=Column(Integer,ForeignKey('inscripciones.id'),nullable=False,index=True)
    status=Column(String(24),nullable=False)
    reason=Column(String(40),nullable=False,default='no_aplica')
    effective_at=Column(DateTime(timezone=True),nullable=False,index=True)
    recorded_at=Column(DateTime(timezone=True),server_default=func.now())
    recorded_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)
    note=Column(Text,nullable=False,default='')
