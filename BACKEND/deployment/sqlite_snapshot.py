"""Private SQLite backups with a verified read-back; never overwrite a destination."""
import hashlib
import os
from pathlib import Path
import sqlite3


def signature(connection):
    schema=connection.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name").fetchall()
    tables=connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    counts={name:connection.execute('SELECT COUNT(*) FROM "'+name.replace('"','""')+'"').fetchone()[0] for (name,) in tables}
    return schema,counts


def create_snapshot(source,destination):
    source=Path(source).resolve(strict=True)
    destination=Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError('Snapshot destination already exists.')
    # SQLite backup obtains a consistent source snapshot, including WAL contents.
    with sqlite3.connect(source.as_uri()+'?mode=ro',uri=True) as live:
        with open(destination,'x',opener=lambda name,flags:os.open(name,flags,0o600)):
            pass
        with sqlite3.connect(destination) as backup:
            live.backup(backup)
            if backup.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:
                raise RuntimeError('Snapshot integrity check failed.')
            # Restore to an isolated memory database and verify schema and row counts.
            with sqlite3.connect(':memory:') as restored:
                backup.backup(restored)
                if signature(backup)!=signature(restored):
                    raise RuntimeError('Snapshot restoration differs from its source.')
            tables=len(signature(backup)[1])
    return {'restoration_verified':True,'tables':tables,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}
