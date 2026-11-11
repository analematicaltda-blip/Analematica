"""Bounded, authenticated local SQLite backups; never overwrites a database or key.
Application encryption/signing keys are deliberately not included in the archive.
POSIX directory descriptors are required; this is not a live database replacement tool.
Keep the source directory private: SQLite opens the live database/WAL by pathname.
"""
import argparse
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import re
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


@contextmanager
def pinned_parent(path):
    """Walk without following links; keep the parent descriptor for POSIX I/O."""
    path = Path(os.path.abspath(path))
    descriptor = None
    try:
        if os.name != 'posix':
            raise BackupError('Esta herramienta endurecida requiere descriptores POSIX.')
        descriptor = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
        for part in path.parent.parts[1:]:
            following = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=descriptor)
            os.close(descriptor)
            descriptor = following
        yield descriptor, path.name
    except OSError:
        raise BackupError('No se pudo acceder a un archivo regular sin enlaces.') from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def read_regular(path, limit, private=False):
    with pinned_parent(path) as (parent, name):
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(descriptor, 'rb') as stream:
            metadata = os.fstat(stream.fileno())
            if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > limit:
                raise BackupError('Archivo no regular o demasiado grande.')
            if private and metadata.st_mode & 0o077:
                raise BackupError('La clave debe tener permisos 0600 o más restrictivos.')
            result = stream.read(limit + 1)
            if len(result) > limit:
                raise BackupError('Archivo demasiado grande.')
            return result


def private_key(path):
    key = read_regular(path, 32, private=True)
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
    with pinned_parent(path) as (parent, name):
        created = None
        try:
            descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600, dir_fd=parent)
            with os.fdopen(descriptor, 'wb') as stream:
                metadata = os.fstat(stream.fileno())
                created = (metadata.st_dev, metadata.st_ino)
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            # Do not report success if the visible parent was swapped meanwhile.
            visible = path.parent.stat(follow_symlinks=False)
            held = os.fstat(parent)
            if (visible.st_dev, visible.st_ino) != (held.st_dev, held.st_ino):
                raise BackupError('El directorio de destino cambió durante la escritura.')
            os.fsync(parent)
        except BaseException:
            if created is not None:
                try:
                    current = os.stat(name, dir_fd=parent, follow_symlinks=False)
                    if (current.st_dev, current.st_ino) == created:
                        os.unlink(name, dir_fd=parent)
                except FileNotFoundError:
                    pass
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


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise BackupError('Cabecera con campos repetidos.')
        result[key] = value
    return result


def reject_constant(value):
    raise BackupError('Cabecera con número no finito.')


def validate_header(header):
    fields = {'schema', 'service', 'created_at', 'bytes', 'tables', 'sha256',
              'application_keys_included'}
    if not isinstance(header, dict) or set(header) != fields:
        raise BackupError('Campos de cabecera inválidos.')
    if (type(header['bytes']) is not int or not 0 < header['bytes'] <= MAX_DATABASE
            or type(header['tables']) is not int or not 0 <= header['tables'] <= MAX_DATABASE
            or not isinstance(header['sha256'], str)
            or re.fullmatch(r'[0-9a-f]{64}', header['sha256']) is None):
        raise BackupError('Tipos de cabecera inválidos.')
    timestamp = header['created_at']
    if not isinstance(timestamp, str) or len(timestamp) > 40:
        raise BackupError('Fecha de cabecera inválida.')
    parsed = datetime.fromisoformat(timestamp)
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise BackupError('La fecha de respaldo debe incluir zona UTC.')


def decrypt(archive, key_file, expected_service):
    if expected_service not in SERVICES:
        raise BackupError('Servicio no reconocido.')
    data = read_regular(archive, MAX_ARCHIVE)
    if len(data) > MAX_ARCHIVE or not data.startswith(MAGIC):
        raise BackupError('Formato de respaldo inválido.')
    offset = len(MAGIC)
    try:
        length = struct.unpack('>I', data[offset:offset+4])[0]
        if length <= 0 or length > MAX_HEADER:
            raise BackupError('Cabecera de respaldo inválida.')
        start = offset + 4; end = start + length
        header = json.loads(data[start:end], object_pairs_hook=strict_pairs,
                            parse_constant=reject_constant)
        validate_header(header)
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
