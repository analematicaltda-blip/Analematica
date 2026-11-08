"""Restore a real ContentDraft table to a new isolated SQLite database, not in place."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'BACKEND/SGA-CD-BACKEND'), str(ROOT/'BACKEND/SGA-CD-BACKEND/tests'), str(ROOT/'BACKEND/deployment')]
os.environ['DATABASE_URL'] = 'sqlite://'
os.environ['SECRET_KEY'] = 'isolated-restore-fixture-not-a-deployed-secret'
# Importing the established fixture registers the actual SQLAlchemy foreign-key graph.
import test_assistance
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models.assistance import ContentDraft
from app.models.user import Usuario, RolesEnum
from app.models.tenancy import Inquilino
from app.services.assistance import control_crypto, content
from app.services.assistance.engine import Actor
from encrypted_backup import keygen, backup, verify, restore


def run():
    with tempfile.TemporaryDirectory(prefix='editorial-restore-') as private:
        root = Path(private); source = root/'source.sqlite3'; snapshot = root/'snapshot.sgacdb'; restored = root/'restored.sqlite3'
        with patch.dict(os.environ, {'ASSISTANCE_CONTROL_KEY_DIR':str(root/'keys'), 'ASSISTANCE_CONTENT_ENABLED':'1'}):
            control_crypto.initialize()
            original_key_hash = hashlib.sha256((root/'keys/data.key').read_bytes()).hexdigest()
            engine = create_engine('sqlite:///' + str(source))
            # The foreign-key graph is registered, but only these real domain tables are needed.
            for model in [Inquilino, Usuario, ContentDraft]:
                model.__table__.create(engine)
            from app.models.user import Role, user_roles_association
            Role.__table__.create(engine); user_roles_association.create(engine)
            try:
                with Session(engine, expire_on_commit=False) as db:
                    db.add(Inquilino(id=1,nombre_empresa='Restore fixture',activo=True))
                    db.add(Usuario(id=1,inquilino_id=1,nombre_usuario='restore-fixture',password_hash='fixture-not-a-login',rol=RolesEnum.admin_empresa,activo=True));db.commit()
                    who=Actor(1,1)
                    draft=content.create(db,who,'meta','Brief público sintético','Texto de prueba para restauración')
                    reviewed=content.review(db,who,draft['id'],draft['revision'],draft['digest'],True)
                    expected=content.export(db,who,draft['id'])
                before=hashlib.sha256(source.read_bytes()).hexdigest()
                backup_key=root/'backup.key';keygen(backup_key)
                first=backup(source,snapshot,backup_key,'sgacd')
                verified=verify(snapshot,backup_key,'sgacd')
                second=restore(snapshot,restored,backup_key,'sgacd')
                assert hashlib.sha256(source.read_bytes()).hexdigest()==before
                restored_engine=create_engine('sqlite:///' + str(restored))
                try:
                    with Session(restored_engine) as db:
                        actual=content.export(db,who,draft['id'])
                        assert actual==expected
                        assert db.query(ContentDraft).count()==1
                        raw=db.get(ContentDraft,draft['id']).content
                        assert 'Texto de prueba' not in raw
                    with sqlite3.connect(restored) as db:
                        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
                        assert db.execute('PRAGMA integrity_check').fetchall()==[('ok',)]
                    assert hashlib.sha256((root/'keys/data.key').read_bytes()).hexdigest()==original_key_hash
                    result={'isolated_fixture':True,'new_database_restored':True,'source_unchanged':True,
                            'actual_model':'ContentDraft','encrypted_text_recovered_with_original_key':True,
                            'reviewed_version_preserved':actual['revision']==reviewed['revision'],
                            'foreign_keys_valid':True,'publication_enabled':actual['publication_enabled'],
                            'snapshot_private':(snapshot.stat().st_mode&0o777)==0o600,
                            'tables':first['tables'],'restore_verified':verified['verified'],
                            'backup_encrypted':first['encrypted'],
                            'archive_application_keys_included':first['application_keys_included']}
                finally:
                    restored_engine.dispose()
            finally:
                engine.dispose()
    return result

if __name__ == '__main__':
    print(json.dumps(run(),sort_keys=True))
