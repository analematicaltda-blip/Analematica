from sqlalchemy.orm import Session
import sys
from pathlib import Path

# Add SGA-CD-DB.git to path if needed for settings model
db_git_path = Path(__file__).resolve().parents[3] / "SGA-CD-DB.git"
if str(db_git_path) not in sys.path:
    sys.path.insert(0, str(db_git_path))

try:
    from models import settings as models
except ImportError:
    from app.models import base as models_base
    from sqlalchemy import Column, String, Text
    class Setting(models_base.Base):
        __tablename__ = "settings"
        key = Column(String, primary_key=True, index=True)
        value = Column(Text, nullable=False)
    class models:
        Setting = Setting

def get_setting(db: Session, key: str) -> models.Setting | None:
    """
    Retrieves a setting from the database by its key.
    """
    return db.query(models.Setting).filter(models.Setting.key == key).first()

def update_setting(db: Session, key: str, value: str) -> models.Setting:
    """
    Creates or updates a setting in the database.
    """
    db_setting = get_setting(db, key)
    if db_setting:
        db_setting.value = value
    else:
        db_setting = models.Setting(key=key, value=value)
        db.add(db_setting)

    db.commit()
    db.refresh(db_setting)
    return db_setting
