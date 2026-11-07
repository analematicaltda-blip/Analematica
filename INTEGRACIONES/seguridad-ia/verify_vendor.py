"""Verify exact copied upstream files, modes and Git blob hashes, without executing them."""
import hashlib
import json
import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def verify():
    for name in ['aisoc','free-ai-apis']:
        manifest=json.loads((Path(__file__).parent/(name+'-upstream.json')).read_text())
        target=ROOT/manifest['destination'];expected=set()
        for entry in manifest['files']:
            rel=entry['path'];expected.add(rel);p=target/rel
            assert p.exists() or p.is_symlink(),rel
            assert p.is_symlink()==(entry['mode']=='120000'),rel
            data=os.readlink(p).encode() if p.is_symlink() else p.read_bytes()
            assert hashlib.sha256(data).hexdigest()==entry['sha256'],rel
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==entry['git_blob'],rel
            if os.name!='nt' and not p.is_symlink():assert bool(p.stat().st_mode&0o111)==(entry['mode']=='100755'),rel
        actual={str(p.relative_to(target)) for p in target.rglob('*') if p.is_file() or p.is_symlink()}
        assert actual==expected,(actual-expected,expected-actual)
        print(name+': '+str(len(expected))+' exact files; '+manifest['license']+'; '+manifest['commit'])

if __name__=='__main__':verify()
