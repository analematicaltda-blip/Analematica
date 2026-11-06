"""Generate private local test configuration once; never overwrite credentials."""
import argparse
import base64
import json
import os
from pathlib import Path
import secrets

ROOT = Path(__file__).resolve().parent

def initialize(directory=ROOT / '.runtime'):
    directory = Path(directory)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    pending = {}
    for name in ['sgacd', 'erp-tur', 'turismo']:
        dbfile = directory / (name + '-db.env')
        if dbfile.exists():
            database = dict(line.split('=', 1) for line in dbfile.read_text().splitlines() if '=' in line and not line.startswith('#'))
        else:
            database = {'POSTGRES_DB': name.replace('-', '_'), 'POSTGRES_USER': 'backend', 'POSTGRES_PASSWORD': secrets.token_hex(32)}
            pending[dbfile] = database
        servicefile = directory / (name + '.env')
        if servicefile.exists():
            continue
        url = f"postgresql://{database['POSTGRES_USER']}:{database['POSTGRES_PASSWORD']}@{name}-db:5432/{database['POSTGRES_DB']}"
        if name == 'sgacd':
            config = {'DATABASE_URL': url.replace('postgresql://', 'postgresql+psycopg2://'), 'SECRET_KEY': secrets.token_hex(48), 'ENVIRONMENT': 'local', 'SGACD_INIT_SCHEMA': '0', 'OPENAI_API_KEY': '', 'BACKEND_CORS_ORIGINS': '["http://localhost:3000","http://127.0.0.1:3000"]'}
        else:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            private = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
            public = key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
            config = {'DJANGO_JWT_PRIVATE_KEY_B64': base64.b64encode(private).decode(), 'DJANGO_JWT_PUBLIC_KEY_B64': base64.b64encode(public).decode(), 'DATABASE_URL': url, 'DJANGO_SECRET_KEY': secrets.token_hex(48), 'DJANGO_FIELD_ENCRYPTION_KEY': base64.urlsafe_b64encode(secrets.token_bytes(32)).decode(), 'DJANGO_ALLOWED_HOSTS': 'localhost,127.0.0.1', 'REDIS_URL': 'redis://redis:6379/' + ('1' if name == 'erp-tur' else '2'), 'DJANGO_MIGRATE': '0'}
        pending[servicefile] = config
    pending[directory / 'analematica.env'] = {'SGACD_API_URL': 'http://sgacd:8000'}
    for path, config in pending.items():
        if path.exists():
            continue
        with open(path, 'x', opener=lambda name, flags: os.open(name, flags, 0o600)) as stream:
            stream.write(''.join(key + '=' + value + '\n' for key, value in config.items()))
    print('Configuración local preparada. Las claves existentes se conservaron; no se iniciaron servicios.')

if __name__ == '__main__':
    initialize()
