"""Generate the actual preview Nginx configuration in a private test directory."""
import argparse,importlib.util,ipaddress,os
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,required=True);parser.add_argument('--backend',required=True);args=parser.parse_args()
host,port=args.backend.rsplit(':',1)
if not ipaddress.ip_address(host).is_private or not 1<=int(port)<=65535:raise ValueError('Private fixture address required')
spec=importlib.util.spec_from_file_location('preview_test',Path(__file__).resolve().parents[1]/'prepare.py');preview=importlib.util.module_from_spec(spec);spec.loader.exec_module(preview)
preview.PRIVATE=args.directory/'private';preview.RUNTIME=args.directory/'runtime'
preview.PRIVATE.mkdir(mode=0o700);preview.RUNTIME.mkdir(mode=0o700)
preview.certificate();preview.credentials();os.environ['SGACD_ENABLE_ERP_API']='1';preview.nginx()
path=preview.RUNTIME/'nginx.conf';text=path.read_text()
text=text.replace('erp-tur:8000',args.backend).replace('http://erp-web:3000','http://'+args.backend).replace('http://turismo-web:3000','http://'+args.backend)
path.write_text(text)
