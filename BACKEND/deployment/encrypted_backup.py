"""Bounded, authenticated local SQLite backups; never overwrites a database or key.
Application encryption/signing keys are deliberately not included in the archive.
"""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import struct
import sys
import time

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

MAGIC = b'SGACD-BACKUP-1\n'
MAX_DATABASE = 64 * 1024 * 1024
MAX_HEADER = 4096
MAX_ARCHIVE = MAX_DATABASE + MAX_HEADER + 1024
SERVICES = {'sgacd', 'analematica', 'erp-tur', 'turismo'}
ROOT = Path(__file__).resolve().parents[2]

class BackupError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def private_key(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise BackupError('Se requiere un archivo de clave privado existente.')
    if os.name == 'posix' and path.stat().st_mode & 0o077:
        raise BackupError('La clave debe tener permisos 0600 o más restrictivos.')
    with path.open('rb') as stream:
        key = stream.read(33)
    if len(key) != 32:
        raise BackupError('La clave de respaldo debe contener exactamente 32 bytes.')
    return key


def fresh_destination(path):
    path = Path(path)
    if path.exists() or path.is_symlink():
        raise BackupError('El destino ya existe; utiliza una ruta nueva.')
    resolved = path.resolve()
    if (resolved.is_relative_to(ROOT)
            and not any(resolved.is_relative_to(allowed) for allowed in [ROOT / '.runtime', ROOT / 'BACKEND/deployment/.runtime'])):
        raise BackupError('Guarda claves y copias fuera del código o dentro de .runtime ignorado.')
    if not path.parent.is_dir():
        raise BackupError('El directorio de destino debe existir.')
    if any(parent.is_symlink() for parent in path.absolute().parents):
        raise BackupError('No uses directorios de destino enlazados simbólicamente.')
    return path


def write_exclusive(path, data):
    path = fresh_destination(path)
    created = False
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
    except BaseException:
        if created:
            path.unlink(missing_ok=True)
        raise
    return path


def keygen(path):
    write_exclusive(path, os.urandom(32))
    return {'created': True, 'key_printed': False}


def inspect(connection):
    connection.execute('PRAGMA trusted_schema=OFF')
    if connection.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
        raise BackupError('La base no superó la comprobación de integridad.')
    if connection.execute('PRAGMA foreign_key_check').fetchall():
        raise BackupError('La base contiene relaciones inválidas.')
    return connection.execute("SELECT count(*) FROM sqlite_master WHERE type='table'").fetchone()[0]


def snapshot(source):
    source = Path(source)
    if source.is_symlink() or not source.is_file():
        raise BackupError('Se requiere una base SQLite local existente, sin enlace simbólico.')
    source = source.resolve(strict=True)
    if source.stat().st_size > MAX_DATABASE:
        raise BackupError('La base excede el límite de 64 MiB de esta herramienta local.')
    started = time.monotonic()
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True, timeout=5)) as live:
        page_size = live.execute('PRAGMA page_size').fetchone()[0]
        with closing(sqlite3.connect(':memory:')) as copied:
            def progress(status, remaining, total):
                # Conservative allowance for the largest SQLite page size, including WAL growth.
                if time.monotonic() - started > 60:
                    raise BackupError('La copia excedió el tiempo máximo permitido.')
                if total * page_size > MAX_DATABASE:
                    raise BackupError('La instantánea excede el límite de 64 MiB.')
            live.backup(copied, pages=256, progress=progress)
            tables = inspect(copied)
            payload = copied.serialize()
            # SQLite backup merged all committed WAL pages into this standalone image.
            # sqlite3_deserialize cannot open WAL-mode images: SQLite format bytes
            # 18/19 are read/write versions (1=rollback journal, 2=WAL).
            # Normalize only the copied header, never the live database.
            if payload.startswith(b'SQLite format 3\x00') and payload[18:20] == b'\x02\x02':
                payload = payload[:18] + b'\x01\x01' + payload[20:]
            with closing(sqlite3.connect(':memory:')) as verified:
                verified.deserialize(payload)
                if inspect(verified) != tables:
                    raise BackupError('La instantánea autocontenida no pudo verificarse.')
    if len(payload) > MAX_DATABASE:
        raise BackupError('La instantánea excede el límite permitido.')
    return payload, tables


def backup(source, destination, key_file, service):
    if service not in SERVICES:
        raise BackupError('Servicio no reconocido.')
    fresh_destination(destination)
    key = private_key(key_file)
    payload, tables = snapshot(source)
    header = {'schema': 'sgacd-sqlite-backup-v1', 'service': service,
              'created_at': datetime.now(timezone.utc).isoformat(),
              'bytes': len(payload), 'tables': tables,
              'sha256': hashlib.sha256(payload).hexdigest(), 'application_keys_included': False}
    encoded = canonical(header)
    nonce = os.urandom(12)
    prefix = MAGIC + struct.pack('>I', len(encoded)) + encoded
    sealed = prefix + nonce + AESGCM(key).encrypt(nonce, payload, prefix)
    write_exclusive(destination, sealed)
    return {'service': service, 'encrypted': True, 'tables': tables,
            'archive_sha256': hashlib.sha256(sealed).hexdigest(),
            'application_keys_included': False}


def decrypt(archive, key_file, expected_service):
    if expected_service not in SERVICES:
        raise BackupError('Servicio no reconocido.')
    path = Path(archive)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_ARCHIVE:
        raise BackupError('Archivo de respaldo inexistente, enlazado o demasiado grande.')
    with path.open('rb') as stream:
        data = stream.read(MAX_ARCHIVE + 1)
    if len(data) > MAX_ARCHIVE or not data.startswith(MAGIC):
        raise BackupError('Formato de respaldo inválido.')
    offset = len(MAGIC)
    try:
        length = struct.unpack('>I', data[offset:offset+4])[0]
        if length <= 0 or length > MAX_HEADER:
            raise BackupError('Cabecera de respaldo inválida.')
        start = offset + 4; end = start + length
        header = json.loads(data[start:end])
        if (not isinstance(header, dict) or header.get('schema') != 'sgacd-sqlite-backup-v1'
                or header.get('service') != expected_service
                or header.get('application_keys_included') is not False):
            raise BackupError('El respaldo no corresponde al servicio esperado.')
        payload = AESGCM(private_key(key_file)).decrypt(data[end:end+12], data[end+12:], data[:end])
        if (len(payload) > MAX_DATABASE or header.get('bytes') != len(payload)
                or hashlib.sha256(payload).hexdigest() != header.get('sha256')):
            raise BackupError('El contenido no coincide con la cabecera autenticada.')
        with closing(sqlite3.connect(':memory:')) as db:
            db.deserialize(payload)
            tables = inspect(db)
        if tables != header.get('tables'):
            raise BackupError('La estructura no coincide con el respaldo.')
    except (InvalidTag, ValueError, struct.error, TypeError, sqlite3.Error):
        raise BackupError('No se pudo autenticar o verificar el respaldo.') from None
    return payload, header, hashlib.sha256(data).hexdigest()


def verify(archive, key_file, expected_service):
    _, header, archive_hash = decrypt(archive, key_file, expected_service)
    return {'verified': True, 'service': header['service'], 'tables': header['tables'],
            'archive_sha256': archive_hash, 'application_keys_included': False}


def restore(archive, destination, key_file, expected_service):
    fresh_destination(destination)
    for suffix in ('-wal', '-shm', '-journal'):
        sidecar = Path(str(destination) + suffix)
        if sidecar.exists() or sidecar.is_symlink():
            raise BackupError('El destino tiene archivos SQLite auxiliares existentes.')
    payload, header, archive_hash = decrypt(archive, key_file, expected_service)
    # Authentication, SQLite integrity and foreign keys were checked entirely in RAM.
    # Only the requested new destination receives a plaintext database, with private permissions.
    write_exclusive(destination, payload)
    return {'restored_to_new_database': True, 'service': header['service'],
            'tables': header['tables'], 'archive_sha256': archive_hash,
            'application_keys_included': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['keygen', 'backup', 'verify', 'restore'])
    parser.add_argument('--key-file', type=Path, required=True)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--destination', type=Path)
    parser.add_argument('--service', choices=sorted(SERVICES))
    args = parser.parse_args()
    try:
        if args.action == 'keygen':
            result = keygen(args.key_file)
        else:
            if not args.service:
                parser.error('--service es obligatorio')
            if args.action == 'backup':
                if not args.source or not args.destination: parser.error('--source y --destination son obligatorios')
                result = backup(args.source, args.destination, args.key_file, args.service)
            else:
                if not args.archive: parser.error('--archive es obligatorio')
                if args.action == 'restore':
                    if not args.destination: parser.error('--destination es obligatorio')
                    result = restore(args.archive, args.destination, args.key_file, args.service)
                else:
                    result = verify(args.archive, args.key_file, args.service)
        print(json.dumps(result, sort_keys=True)); return 0
    except (BackupError, OSError, sqlite3.Error):
        # No connection strings, raw paths, keys or SQLite contents in shared stdout/stderr.
        print('Operación rechazada: revisa formato, permisos, clave, servicio y destinos nuevos.', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
