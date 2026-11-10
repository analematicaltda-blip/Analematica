"""Reproduce isolated accounting suites with at most four test processes.
No production DB, dependency installation, Git changes or provider calls.
"""
import concurrent.futures,hashlib,json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'INTEGRACIONES/operacion'))
import verify_local as runner

def main():
    output=Path(sys.argv[1]).resolve()
    if output.exists() or output.is_relative_to(ROOT):raise SystemExit('Use a new private output directory outside the repository.')
    output.mkdir(mode=0o700)
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'BACKEND/SGA-CD-BACKEND'),DATABASE_URL='sqlite://',SECRET_KEY='isolated-quality-test-not-a-deployed-secret',ASSISTANCE_CONTENT_ENABLED='0',ASSISTANCE_CONTENT_OLLAMA_ENABLED='0',ASSISTANCE_DUET_ENABLED='0',NEXT_TELEMETRY_DISABLED='1')
    before=runner.source_manifest()
    runner.write_private(output/'source-manifest.json',json.dumps(before,indent=2).encode())
    def check(item):
        name,argv,kind,timeout=item
        result=runner.execute(name,argv,output,env,max(timeout,600) if name=='accounting_corporate_bridge' else timeout,kind)
        print(name+': '+result['status'],flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(check,runner.suites(['accounting'],sys.executable,None,output)))
    after=runner.digest(runner.source_manifest());stable=runner.digest(before)==after
    passed=all(r['status']=='PASSED' for r in results) and stable
    report={'schema':'sgacd-recovery-regression-v1','workers':4,'source_digest_before':runner.digest(before),'source_digest_after':after,'source_stable':stable,'local_checks_complete':passed,'production_ready':False,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'results':results}
    runner.write_private(output/'report.json',json.dumps(report,indent=2).encode())
    print(json.dumps({'passed':passed,'suites':len(results),'tests':sum(r.get('tests',0) for r in results),'source_stable':stable}),flush=True)
    return 0 if passed else 2
if __name__=='__main__':raise SystemExit(main())
