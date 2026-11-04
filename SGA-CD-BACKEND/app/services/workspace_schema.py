"""Explicit, additive installation; never recreates or deletes application tables."""
import app.models
from app.models.workspace import WorkspaceGrant,WorkspaceAsset,WorkspaceLead,WorkspaceChannel
from app.db.session import engine
from app.models.corporate import CorporatePage,CorporateOwner,CorporateCommand

def install():
    for model in [WorkspaceGrant,WorkspaceAsset,WorkspaceLead,WorkspaceChannel,CorporatePage,CorporateOwner,CorporateCommand]:model.__table__.create(engine,checkfirst=True)
    from app.services.corporate_commands import Setting
    Setting.__table__.create(engine,checkfirst=True)
    from app.services.corporate_policy import bootstrap_owner
    from app.db.session import SessionLocal
    with SessionLocal() as db:bootstrap_owner(db)
    print('Tablas administrativas preparadas sin eliminar datos existentes.')
if __name__=='__main__':install()
