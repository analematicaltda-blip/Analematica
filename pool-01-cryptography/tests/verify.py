"""Compile real Java cryptography, optionally compile Android, and cross-check with Python."""
import argparse
import hashlib
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--android-jar',type=Path)
args=parser.parse_args()
compiler=[shutil.which('javac')] if shutil.which('javac') else ['java','-m','jdk.compiler/com.sun.tools.javac.Main']
source=ROOT/'android/src/main/java/co/analematica/vault'
with tempfile.TemporaryDirectory(prefix='sgacd-vault-check-') as directory:
    output=Path(directory)
    files=list(source.glob('*.java')) if args.android_jar else [source/'VaultEnvelope.java',source/'PasswordKdf.java']
    if args.android_jar: files+=list((ROOT.parent/'pool-03-integrity/android/src/main/java/co/analematica/integrity').glob('*.java'))
    if args.android_jar: files+=list((ROOT.parent/'pool-04-anti-phishing/android/src/main/java/co/analematica/protection').glob('*.java'))
    flags=['-cp',str(args.android_jar)] if args.android_jar else []
    subprocess.run([*compiler,'-source','17','-target','17','-Xlint:all,-options',*flags,'-d',str(output),*map(str,files),str(ROOT/'tests/java/co/analematica/vault/VaultCryptoCheck.java')],check=True,timeout=60)
    subprocess.run(['java','-cp',str(output),'co.analematica.vault.VaultCryptoCheck',str(output/'envelope.bin'),str(output/'derived.bin')],check=True,timeout=60)
    encoded=(output/'envelope.bin').read_bytes()
    offset=9
    for maximum in [256,128,1024]:
        size=struct.unpack('>H',encoded[offset:offset+2])[0]
        assert size<=maximum
        offset+=2+size
    nonce=encoded[offset:offset+12];offset+=12
    size=struct.unpack('>I',encoded[offset:offset+4])[0];offset+=4
    assert size==len(encoded)-offset
    assert AESGCM(bytes(32)).decrypt(nonce,encoded[offset:],encoded[:offset])==b'public synthetic identity document'
    expected=hashlib.pbkdf2_hmac('sha256',b'integration-passphrase',bytes(range(16)),600_000,dklen=32)
    assert (output/'derived.bin').read_bytes()==expected
print('Python/JCE interoperability verified (AES-256-GCM and PBKDF2-SHA256).')
print('Android API compilation: '+('passed; hardware not exercised' if args.android_jar else 'not requested'))
