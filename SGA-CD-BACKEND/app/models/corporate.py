"""Corporate public content; separate from tenant settings and credentials."""
from sqlalchemy import Column,String,Integer,Text,ForeignKey,DateTime
from sqlalchemy.sql import func
from .base import Base
class CorporatePage(Base):
    __tablename__='corporate_pages'
    key=Column(String(40),primary_key=True)
    payload=Column(Text,nullable=False,default='{}')
    revision=Column(Integer,nullable=False,default=1)
    updated_by=Column(Integer,ForeignKey('usuarios.id'),nullable=False)
    updated_at=Column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
