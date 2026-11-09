"""Interactive encrypted-package laboratory receipt verification on customer host."""
import argparse,getpass,json,sys
from sign_local import bounded
from package_crypto import open_package
from receipt_validation import checked_profile,verify_receipt

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for field in ['input','profile','leaf','root']:parser.add_argument('--'+field,required=True)
    args=parser.parse_args()
    if not sys.stdin.isatty():raise ValueError('Interactive local terminal required.')
    profile=checked_profile(json.loads(bounded(args.profile,16384,True)))
    package=json.loads(bounded(args.input,1500000,True))
    password=getpass.getpass('Contraseña local del paquete de acuse: ')
    raw,_=open_package(package,password,{k:profile[k] for k in ('company_id','document_id')})
    report=verify_receipt(raw,profile=profile,leaf_pem=bounded(args.leaf,16384),root_pem=bounded(args.root,16384))
    print(json.dumps(report,sort_keys=True));print('Verificación SOLO DE LABORATORIO. No acredita origen ni aceptación DIAN. No se envió ni contabilizó ningún documento.')
if __name__=='__main__':
    try:main()
    except Exception:print('Verificación local abortada: revisa paquete, contexto, certificado y firma. No se aceptó ni envió un documento fiscal.',file=sys.stderr);sys.exit(1)
