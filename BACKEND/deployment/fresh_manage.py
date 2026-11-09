"""Django management entry point for an explicitly selected fresh local install."""
import argparse
import sys
from fresh_local import configure

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',required=True)
    parser.add_argument('--service',required=True,choices=['erp-tur','turismo'])
    parser.add_argument('command',choices=['check','showmigrations','migrate','createsuperuser','review_company_link','encrypt_mfa_secrets','purge_totp_enrollments','accounting_project','accounting_db_privileges','accounting_runtime_profile','accounting_reconciliation','runserver'])
    parser.add_argument('arguments',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    if args.command=='runserver':
        # Loopback only; Secure cookies can be opted in for an HTTPS reverse proxy.
        address=next((value for value in args.arguments if not value.startswith('-')), '127.0.0.1:8000')
        if ':' in address and address.rsplit(':',1)[0] not in {'127.0.0.1','localhost','[::1]'}:
            parser.error('fresh-local runserver only accepts a loopback address')
    configure(args.directory,args.service)
    from django.core.management import execute_from_command_line
    execute_from_command_line([sys.argv[0],args.command,*args.arguments])
