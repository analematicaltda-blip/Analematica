from sqlalchemy import Column, String, Text
from .base import Base

class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True, index=True)
    value = Column(Text, nullable=False)
