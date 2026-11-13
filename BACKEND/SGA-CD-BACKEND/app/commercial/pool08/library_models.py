"""Owned landing page state and append-only audit records."""
from sqlalchemy import Column,String,Integer,JSON,Boolean,UniqueConstraint,LargeBinary
from app.models.base import Base
class LibraryItem(Base):
    __tablename__='sga_media_library'
    __table_args__=(UniqueConstraint('scope','code',name='sga_library_scope_code'),)
    id=Column(String(36),primary_key=True)
    scope=Column(String(96),nullable=False,index=True)
    code=Column(String(100),nullable=False,index=True)
    revision=Column(Integer,nullable=False)
    status=Column(String(20),nullable=False,index=True)
    document=Column(JSON,nullable=False)
    document_digest=Column(String(64),nullable=False)
class LibraryEvent(Base):
    __tablename__='sga_media_library_event'
    sequence=Column(Integer,primary_key=True,autoincrement=True)
    id=Column(String(36),nullable=False,unique=True)
    scope=Column(String(96),nullable=False,index=True)
    item_id=Column(String(36),nullable=True,index=True)
    document=Column(JSON,nullable=False)


class LibraryBlob(Base):
    __tablename__='sga_media_library_blob'
    id=Column(String(36),primary_key=True)
    scope=Column(String(96),nullable=False,index=True)
    original=Column(LargeBinary,nullable=False)
    delivery=Column(LargeBinary,nullable=False)
    original_sha=Column(String(64),nullable=False)
    delivery_sha=Column(String(64),nullable=False)
    mime=Column(String(40),nullable=False)
