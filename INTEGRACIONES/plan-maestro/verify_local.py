"""Repeat isolated foundation checks; does not deploy, migrate or contact providers."""
import argparse,json,os,re,subprocess,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SUITES={
 'verified_email_recovery':(['BACKEND/deployment/tests/password_recovery_check.py'],{}),
 'company_scope':(['BACKEND/deployment/tests/company_scope_check.py'],{}),
 'capacity_holds':(['BACKEND/deployment/tests/availability_check.py'],{}),
 'corporate_gateway':(['-m','unittest','discover','-s','BACKEND/deployment/tests','-p','test_local_deployment.py'],{}),
 'institutional_permissions':(['BACKEND/deployment/tests/domain_security_check.py'],{}),
 'provider_isolation':(['BACKEND/deployment/tests/provider_security_check.py'],{}),
 'erp_session':(['BACKEND/deployment/tests/erp_session_check.py'],{}),
 'company_identity':(['BACKEND/deployment/tests/company_identity_check.py'],{}),
 'erp_customer':(['BACKEND/deployment/tests/erp_customer_check.py'],{}),
 'erp_startup':(['BACKEND/deployment/tests/tourism_runtime_check.py'],{'CHECK_SERVICE':'erp-tur'}),
 'tourism_startup':(['BACKEND/deployment/tests/tourism_runtime_check.py'],{'CHECK_SERVICE':'turismo'}),
 'wallet_access':(['WALLET-BACKEND/tests/access_policy_check.py'],{}),
 'central_contract':(['-m','unittest','discover','-s','BACKEND/SGA-CD-BACKEND/tests','-p','test_platform.py'],{'PYTHONPATH':str(ROOT/'BACKEND/SGA-CD-BACKEND')}),
}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 # Never overwrite a prior evidence report silently.
 if args.output.exists():parser.error('El informe de destino ya existe; utilice otro nombre.')
 results=[]
 with tempfile.TemporaryDirectory(prefix='sgacd-plan-check-') as temp:
  for name,(command,extra) in SUITES.items():
   env={**os.environ,**extra,'PYTHONDONTWRITEBYTECODE':'1'}
   with (Path(temp)/name).open('w+') as log:
    try:
     process=subprocess.run([sys.executable,*command],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
     log.seek(0);body=log.read();counts=re.findall(r'Ran (\d+) tests?',body)
     passed=process.returncode==0 and bool(counts) and re.search(r'^OK(?:\s|$)',body,re.M) is not None
     result={'suite':name,'status':'PASSED' if passed else 'FAILED','tests':int(counts[-1]) if counts else 0,'exit_code':process.returncode}
    except subprocess.TimeoutExpired:result={'suite':name,'status':'TIMEOUT','tests':0}
   results.append(result);print(json.dumps(result),flush=True)
 report={'checked_at':datetime.now(timezone.utc).isoformat(),'scope':'isolated foundation contracts; not browser or production certification','production_ready':False,'results':results,'all_passed':all(x['status']=='PASSED' for x in results)}
 args.output.parent.mkdir(parents=True,exist_ok=True)
 with args.output.open('x') as target:json.dump(report,target,indent=2);target.write('\n')
 return 0 if report['all_passed'] else 1
if __name__=='__main__':raise SystemExit(main())
