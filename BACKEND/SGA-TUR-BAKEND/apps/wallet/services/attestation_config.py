"""Read operator-controlled local policy and fresh revocation snapshots.

No HTTPS downloads or trust-on-first-use. Snapshot provenance must be verified
by the operator's feed ingestion workflow. Missing/stale data fails closed.
"""
from datetime import datetime
from pathlib import Path
import hashlib
import json
import re
from .android_attestation import AndroidAttestationPolicy,AndroidAttestationVerifier,RevocationSnapshot,AttestationRejected


def read_json(path,limit):
    path=Path(path)
    if not path.is_absolute() or path.is_symlink() or not path.is_file() or path.stat().st_size>limit:raise AttestationRejected('CONFIGURATION_FILE_INVALID')
    with path.open('rb') as stream:
        raw=stream.read(limit+1)
    if len(raw)>limit:raise AttestationRejected('CONFIGURATION_FILE_INVALID')
    try:return json.loads(raw)
    except (ValueError,UnicodeError):raise AttestationRejected('CONFIGURATION_JSON_INVALID')


def read_snapshot(path):
    value=read_json(path,1048576)
    try:
        if not isinstance(value,dict) or set(value)!={'observed_at','valid_until','revoked_serial_numbers'} or not isinstance(value['revoked_serial_numbers'],list) or len(value['revoked_serial_numbers'])>16384:raise ValueError()
        serials=value['revoked_serial_numbers']
        if any(not isinstance(serial,str) or re.fullmatch('[1-9a-f][0-9a-f]{0,39}',serial) is None for serial in serials):raise ValueError()
        return RevocationSnapshot(datetime.fromisoformat(value['observed_at']),datetime.fromisoformat(value['valid_until']),frozenset(int(serial,16) for serial in serials))
    except (ValueError,TypeError):raise AttestationRejected('REVOCATION_FILE_INVALID')


def load_android_verifier(path):
    value=read_json(path,65536)
    try:
        if not isinstance(value,dict) or set(value)!={'trusted_roots','package_name','signer_sha256','minimum_package_version','minimum_os_version','minimum_patch_level','require_strongbox','maximum_patch_age_days','revocations_file'}:raise ValueError()
        roots=value.pop('trusted_roots');snapshot=value.pop('revocations_file')
        if not isinstance(roots,list) or not 1<=len(roots)<=4 or not isinstance(snapshot,str) or not Path(snapshot).is_absolute():raise ValueError()
        certificates=[]
        for entry in roots:
            if not isinstance(entry,dict) or set(entry)!={'path','sha256'}:raise ValueError()
            source=Path(entry['path'])
            if not source.is_absolute() or source.is_symlink() or not source.is_file() or source.stat().st_size>16384:raise ValueError()
            with source.open('rb') as stream:raw=stream.read(16385)
            if len(raw)>16384 or hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError()
            certificates.append(raw)
        pins=value.pop('signer_sha256')
        if not isinstance(pins,list) or len(pins)!=len(set(pins)):raise ValueError()
        policy=AndroidAttestationPolicy(trusted_roots=tuple(certificates),signer_sha256=frozenset(pins),**value)
        # Re-read on every use: a cached startup snapshot must not outlive its feed.
        verifier=AndroidAttestationVerifier(policy,lambda:read_snapshot(snapshot))
        from datetime import timezone
        verifier.snapshot(datetime.now(timezone.utc))
        return verifier
    except AttestationRejected:raise
    except (OSError,KeyError,ValueError,TypeError):raise AttestationRejected('ATTESTATION_CONFIGURATION_INVALID')
