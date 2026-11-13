"""Verify the local signed export with a separately trusted key, then extract an ingest batch.
No HTTP client, credentials, provider execution or automatic transmission.
"""
import argparse
import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

def extract(bundle,trusted_key,expected_tenant):
    if bundle.get('algorithm')!='Ed25519':raise ValueError('Algoritmo no permitido')
    payload=bundle['payload']
    if not isinstance(payload,str) or len(payload.encode())>1_000_000:raise ValueError('Paquete no válido')
    key=load_pem_public_key(trusted_key)
    if not isinstance(key,Ed25519PublicKey):raise ValueError('Clave de confianza no válida')
    key.verify(base64.b64decode(bundle['signature'],validate=True),payload.encode())
    content=json.loads(payload)
    if content.get('schema')!='sgacd-aisoc-audit-export-v1' or content.get('source_tenant_id')!=expected_tenant:raise ValueError('El paquete no pertenece al tenant de origen esperado')
    batch=content['ingest_batch']
    if batch.get('connector_type')!='sgacd_control_audit' or not isinstance(batch.get('events'),list) or len(batch['events'])>100:raise ValueError('Batch no válido')
    return batch

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--bundle',required=True,type=Path);parser.add_argument('--trusted-key',required=True,type=Path);parser.add_argument('--source-tenant',required=True,type=int);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.bundle.stat().st_size>1_500_000:raise SystemExit('Paquete demasiado grande')
    batch=extract(json.loads(args.bundle.read_text()),args.trusted_key.read_bytes(),args.source_tenant)
    # Never replace an existing operator-owned export.
    import os
    with open(args.output,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:json.dump(batch,stream,ensure_ascii=False,indent=2)
    print('Firma y tenant verificados; batch local preparado:',len(batch['events']),'eventos. No se envió a AiSOC.')
if __name__=='__main__':main()
