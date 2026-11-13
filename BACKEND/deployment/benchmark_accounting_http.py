"""Explicit disposable loopback HTTP benchmark. Never accepts a remote origin/DSN.

Client contention is measured against a serialized fixture gateway: the fixture
shares its SQLAlchemy session and must not pretend to be a production ASGI pool.
"""
import argparse,hashlib,importlib.util,json,os,platform,queue,subprocess,sys,tempfile,threading,time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from decimal import Decimal,localcontext,Context
from pathlib import Path
import httpx
from accounting_benchmark_metrics import summarize,classification_metrics
ROOT=Path(__file__).resolve().parents[2]

def validate_reply(flow,raw,company,day):
    if flow not in {'trial_balance','profitability','quick_ratio','commercial_queue'}:raise ValueError('Unsupported measured flow.')
    data=raw.get('data') if isinstance(raw,dict) else None
    if not isinstance(data,dict) or raw.get('company_id')!=company:raise ValueError('Unexpected scoped reply.')
    if flow in {'trial_balance','profitability'}:
        if data.get('tenant_id')!=company or data.get('currency')!='COP' or data.get('snapshot',{}).get('database')!='primary':raise ValueError('Unexpected primary report.')
        if flow=='trial_balance':
            if data.get('total_debit')!='15.00' or data.get('total_credit')!='15.00':raise ValueError('Synthetic book changed.')
        elif data.get('net_profit')!='10.00' or data.get('start_date')!=day or data.get('end_date')!=day:raise ValueError('Synthetic profitability differs.')
    else:
        if data.get('schema')!='sgacd-accounting-query-v1' or data.get('company_id')!=company or data.get('read_only') is not True or any(data.get(k) is not False for k in ['generated_sql','external_model_used','ledger_written','financial_action_authorized']):raise ValueError('Query authority changed.')
        inner=data.get('data',{})
        if flow=='quick_ratio':
            if data.get('intent')!='quick_ratio' or inner.get('value')!='3.0000' or inner.get('cutoff_date')!=day:raise ValueError('Synthetic liquidity differs.')
        elif data.get('intent')!='commercial_queue' or inner.get('fiscal_acceptance')!='NOT_VERIFIED' or inner.get('fiscal_receipt_verified') is not False:raise ValueError('Queue cannot certify DIAN.')

def run(samples=10,clients=1,*,combined_context=False):
    if type(samples) is not int or not 5<=samples<=100 or type(clients) is not int or not 1<=clients<=min(8,samples):raise ValueError('Use5..100 samples per flow and1..8 bounded clients.')
    if type(combined_context) is not bool:raise ValueError('Explicit context mode required.')
    if 'django' in sys.modules:raise ValueError('Use a fresh process and disposable fixture.')
    spec=importlib.util.spec_from_file_location('quality',Path(__file__).resolve().parents[2] / 'BACKEND/INTEGRACIONES/operacion/verify_local.py');quality=importlib.util.module_from_spec(spec);spec.loader.exec_module(quality);before=quality.digest(quality.source_manifest())
    with tempfile.TemporaryDirectory(prefix='acc023-http-') as directory,tempfile.TemporaryFile() as diagnostics:
        private=Path(directory);private.chmod(0o700)
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','ACCOUNTING_HTTP_BENCHMARK_SERIAL':'1','LEDGER_BROWSER':'1','CORPORATE_LEDGER_COMBINED_CONTEXT_ENABLED':'1' if combined_context else '0'}
        process=subprocess.Popen([sys.executable,str(ROOT/'FRONTEND/deployment/tests/corporate_ledger_server.py'),'--assets',str(private)],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=diagnostics,text=True)
        try:
            ready=queue.Queue()
            def reader():
                for line in process.stdout:
                    if line.startswith('READY '):ready.put(int(line.split()[1]));return
            threading.Thread(target=reader,daemon=True).start();port=ready.get(timeout=40)
            if not 1024<=port<=65535:raise ValueError('Invalid local fixture port.')
            origin='http://127.0.0.1:'+str(port);credentials=json.loads((private/'corporate-credentials.json').read_text());day=credentials['recognition']['entry_date']
            # Scope comes from a fixture-provisioned authenticated source, never CLI input.
            headers={'Authorization':'Bearer '+credentials['token'],'Cookie':'sgacd_erp_tur_session='+credentials['erp_cookie']}
            with httpx.Client(base_url=origin,headers=headers,trust_env=False,timeout=15) as client:
                setup=client.get('/api/v1/workspace/corporate/accounting/report',params={'report':'trial_balance','until':day});setup.raise_for_status();company=setup.json()['company_id']
            calls={
                'trial_balance':('GET','/api/v1/workspace/corporate/accounting/report',{'params':{'report':'trial_balance','until':day}}),
                'profitability':('GET','/api/v1/workspace/corporate/accounting/report',{'params':{'report':'profitability','since':day,'until':day}}),
                'quick_ratio':('POST','/api/v1/workspace/corporate/accounting/commands/query',{'json':{'question':'liquidez','until':day}}),
                'commercial_queue':('POST','/api/v1/workspace/corporate/accounting/commands/query',{'json':{'question':'estado de la cola comercial'}})}
            flows={};raw_samples={}
            for flow,(method,path,kwargs) in calls.items():
                def worker(worker_id):
                    results=[]
                    with httpx.Client(base_url=origin,headers=headers,trust_env=False,timeout=15) as client:
                        for index in range(worker_id,samples,clients):
                            start=time.perf_counter_ns();status=None;code=None
                            try:
                                response=client.request(method,path,**kwargs);status=response.status_code
                                if status!=200:code='HTTP_RATE_LIMITED' if status==429 else 'HTTP_STATUS';raise ValueError()
                                try:validate_reply(flow,response.json(),company,day)
                                except (ValueError,TypeError,KeyError,AttributeError):code='INVALID_RESPONSE';raise ValueError() from None
                                ok=True
                            except Exception:ok=False;code=code or 'REQUEST_FAILED'
                            results.append({'index':index,'duration_ns':time.perf_counter_ns()-start,'ok':ok,'http_status':status,'failure_code':code})
                    return results
                begin=time.perf_counter_ns()
                with ThreadPoolExecutor(max_workers=clients) as pool:rows=sorted([row for group in pool.map(worker,range(clients)) for row in group],key=lambda r:r['index'])
                wall=time.perf_counter_ns()-begin;raw_samples[flow]=rows
                with localcontext(Context(prec=40)):rate=format((Decimal(samples)*1000000000/wall).quantize(Decimal('.001')),'.3f')
                flows[flow]={**summarize([{'duration_ns':r['duration_ns'],'ok':r['ok']} for r in rows]),'wall_duration_ns':wall,'attempts_per_second':rate}
            with httpx.Client(base_url=origin,trust_env=False,timeout=15) as anonymous:denied=anonymous.get(calls['trial_balance'][1],params=calls['trial_balance'][2]['params']).status_code
            after=quality.digest(quality.source_manifest());dataset={'schema':'sgacd-synthetic-http-read-v1','flows':list(calls),'samples_per_flow':samples,'client_workers':clients,'server_workers':1,'database':'disposable SQLite fixture','gateway':'serialized HTTP wrapper over in-process ASGI and real ERP HTTP/WSGI','parent_unmeasured_authenticated_setup_requests':1,'fixture_provisioning_login_requests_excluded':True,'combined_context_enabled':combined_context,'rate_limits_preserved':True,'unmeasured_anonymous_control_requests':1,'timed_attempts_discarded':0,'preflight_report_requests_excluded':1,'connection_setup_included':True,'money_executed':False,'ledger_mutation_in_measured_flows':False}
            return {'schema':'sgacd-accounting-http-benchmark-v1','created_at':datetime.now(timezone.utc).isoformat(),'source_digest':before,'source_stable':before==after,'dataset':dataset,'dataset_digest':hashlib.sha256(json.dumps(dataset,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'hardware':{'os':platform.system(),'machine':platform.machine(),'python':platform.python_version(),'logical_cpus_visible':os.cpu_count(),'affinity_cpus_visible':len(os.sched_getaffinity(0)) if hasattr(os,'sched_getaffinity') else None},'flows':flows,'attempts':raw_samples,'security_controls':{'anonymous_status':denied,'anonymous_denied':denied==401},'classification':classification_metrics(None),'production_ready':False,'limits':['Synthetic read-only HTTP calls and client queue contention, not event-to-ledger write latency','One serialized fixture gateway and SQLite; no production worker/database concurrency qualification','ASGI handled in-process behind actual loopback HTTP; ERP uses real HTTP/WSGI','No bank/DIAN/devices, cold process startup or remote network latency included','Shared cloud hardware; local250ms results are not a production SLA','No classifier/model executed; no99.8% precision claim']}
        finally:
            process.terminate()
            try:process.wait(timeout=10)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=5)
            process.stdout.close()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--synthetic-local',action='store_true',required=True);parser.add_argument('--samples',type=int,default=10);parser.add_argument('--clients',type=int,default=1);parser.add_argument('--combined-context',action='store_true');parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();target=args.output
    if not target.is_absolute() or target.resolve().is_relative_to(ROOT) or target.exists() or any(p.is_symlink() for p in [target,*target.parents]):parser.error('Use a new absolute private output outside the repository, without symlinks.')
    result=run(args.samples,args.clients,combined_context=args.combined_context)
    with open(target,'x',opener=lambda name,flags:os.open(name,flags,0o600)) as stream:json.dump(result,stream,ensure_ascii=False,indent=2)
    print(json.dumps({'report':str(target),'source_stable':result['source_stable'],'flows':result['flows'],'classification_status':result['classification']['status'],'production_ready':False}))
    if not result['source_stable'] or not result['security_controls']['anonymous_denied'] or any(r['errors'] for r in result['flows'].values()):raise SystemExit(1)
if __name__=='__main__':main()
