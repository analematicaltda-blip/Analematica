"""Persistent local control keys: no keys are embedded in code, JSON responses or Git."""
import base64
import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import HTTPException

def directory():
    return Path(os.environ.get('ASSISTANCE_CONTROL_KEY_DIR','/state/assistance-control-keys'))

def initialize():
    root=directory();root.mkdir(parents=True,exist_ok=True,mode=0o700)
    entries={'signing.pem':lambda:Ed25519PrivateKey.generate().private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()),'data.key':Fernet.generate_key}
    for name,generate in entries.items():
        path=root/name
        if not path.exists():
            with open(path,'xb',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:stream.write(generate())
    keys()  # refuse malformed existing files instead of replacing them

def keys():
    try:
        root=directory();private=serialization.load_pem_private_key((root/'signing.pem').read_bytes(),password=None)
        if not isinstance(private,Ed25519PrivateKey):raise ValueError('not ed25519')
        return private,Fernet((root/'data.key').read_bytes())
    except (OSError,ValueError,TypeError):
        raise HTTPException(503,'Prepara las claves privadas del control de equipos antes de vincular dispositivos.') from None

def public_key():
    private,_=keys()
    return private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()

def encrypt(text):return keys()[1].encrypt(text.encode()).decode()
def decrypt(text):return keys()[1].decrypt(text.encode()).decode()
def sign(value):
    text=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
    return {'payload':text,'signature':base64.b64encode(keys()[0].sign(text.encode())).decode()}

if __name__=='__main__':
    initialize();print('Claves de control preparadas y conservadas fuera de Git. No se imprimieron secretos.')
