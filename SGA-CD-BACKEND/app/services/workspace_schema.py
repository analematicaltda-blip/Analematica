"""Explicit, additive installation; never recreates or deletes application tables."""
import app.models
from app.models.workspace import WorkspaceGrant,WorkspaceAsset,WorkspaceLead,WorkspaceChannel
from app.db.session import engine
from app.models.corporate import CorporatePage

def install():
    for model in [WorkspaceGrant,WorkspaceAsset,WorkspaceLead,WorkspaceChannel,CorporatePage]:model.__table__.create(engine,checkfirst=True)
    print('Tablas administrativas preparadas sin eliminar datos existentes.')
if __name__=='__main__':install()
