"""Interactive customer-host CLI: encrypted input/output, never an ERP route."""
import argparse,getpass,json,os,sys
from pathlib import Path
from local_signer import profile_checked,parse_invoice,sign_package
from package_crypto import open_package,canonical

def bounded(path,maximum,private=False):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>maximum or private and p.stat().st_mode&0o077:raise ValueError('Bounded private file required.')
    return p.read_bytes()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ['input','profile','key','leaf','root','policy','output']:parser.add_argument('--'+name,required=True)
    args=parser.parse_args()
    if not sys.stdin.isatty():raise ValueError('Interactive local terminal required; no automated signing approvals.')
    profile=profile_checked(json.loads(bounded(args.profile,16384,True)));value=json.loads(bounded(args.input,1500000));password=getpass.getpass('Contraseña local del paquete: ');expected={k:profile[k] for k in ('company_id','document_id')};plain,package=open_package(value,password,expected);parse_invoice(plain,profile)
    print('SOLO LABORATORIO. No emite factura ni valida DIAN. Documento:',profile['document_id']);print('Empresa:',profile['company_id']);print('Paquete revisado:',package['package_digest'])
    source=input('Primera revisión — escribe REVISADO '+package['package_digest'][:12]+': ')
    if source!='REVISADO '+package['package_digest'][:12]:raise ValueError('Source not approved.')
    confirm=input('Segunda autorización — escribe FIRMAR LAB '+profile['document_id']+': ')
    if confirm!='FIRMAR LAB '+profile['document_id']:raise ValueError('Signature not approved.')
    key_password=getpass.getpass('Contraseña de la llave PKCS8 cifrada: ').encode()
    result=sign_package(value,package_password=password,key_pem=bounded(args.key,32768,True),key_password=key_password,leaf_pem=bounded(args.leaf,16384),root_pem=bounded(args.root,16384),policy=bounded(args.policy,1024*1024),profile=profile,source_confirmation=source,sign_confirmation=confirm)
    # Exclusive creation preserves existing packages and never writes clear XML/key.
    created=False
    try:
        fd=os.open(args.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);created=True
        with os.fdopen(fd,'wb') as stream:stream.write(canonical(result['package']));stream.flush();os.fsync(stream.fileno())
    except BaseException:
        if created:Path(args.output).unlink(missing_ok=True)
        raise
    print(json.dumps(result['report'],sort_keys=True));print('Paquete de laboratorio cifrado escrito; no enviado.')
if __name__=='__main__':
    try:main()
    except Exception:print('Firma de laboratorio abortada. Revisa perfil, aprobaciones, claves y archivos; no se emitió ni envió una factura.',file=sys.stderr);sys.exit(1)
