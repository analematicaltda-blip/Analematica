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

class CorporateOwner(Base):
    __tablename__='corporate_owner'
    id=Column(Integer,primary_key=True)
    user_id=Column(Integer,ForeignKey('usuarios.id'),nullable=False,unique=True)
    bound_at=Column(DateTime(timezone=True),server_default=func.now())

class CorporateCommand(Base):
    __tablename__='corporate_commands'
    id=Column(String(36),primary_key=True)
    actor_id=Column(Integer,ForeignKey('usuarios.id'),nullable=False,index=True)
    target=Column(String(20),nullable=False)
    operation=Column(String(80),nullable=False)
    request_hash=Column(String(64),nullable=False)
    status=Column(String(20),nullable=False)
    before=Column(Text,nullable=False,default='{}')
    after=Column(Text,nullable=False,default='{}')
    result=Column(Text,nullable=False,default='{}')
    undone_by=Column(String(36))
    created_at=Column(DateTime(timezone=True),server_default=func.now())
