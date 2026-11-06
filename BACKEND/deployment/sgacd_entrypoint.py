"""Explicit initialization for a new database; normal starts do not migrate data."""
import os
import sys
if os.environ.get('SGACD_INIT_SCHEMA') == '1' or '--init-db' in sys.argv:
    import app.main
    from app.models.base import Base
    from app.db.session import engine
    Base.metadata.create_all(engine)
    from app.services.workspace_schema import install
    install()
    from app.services.assistance.schema import install as install_assistance
    install_assistance()
    from app.services.assistance.control_crypto import initialize as initialize_control
    initialize_control()
    if '--init-db' in sys.argv:
        raise SystemExit(0)
os.execvp('uvicorn', ['uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000'])
