"""Build full generated Next projects, preserving source trees and strict checks."""
import argparse,importlib.util,json,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dependencies',type=Path,required=True,help='Installed node_modules from the canonical lockfile')
    parser.add_argument('--output',type=Path,required=True,help='New private workspace for generated projects, logs and report')
    parser.add_argument('--system',choices=['erp','turismo','both'],default='both')
    args=parser.parse_args();dependencies=args.dependencies.resolve();output=args.output.resolve()
    if output.exists():parser.error('Use a new output directory; existing build evidence is preserved.')
    binary=dependencies/'next/dist/bin/next'
    required=[binary,dependencies/'typescript/bin/tsc',dependencies/'@types/react/index.d.ts',dependencies/'@types/node/index.d.ts']
    if not all(path.is_file() for path in required):parser.error('Install the canonical lockfile with npm ci --include=dev before building.')
    spec=importlib.util.spec_from_file_location('web_preview_builder',HERE/'prepare.py');preview=importlib.util.module_from_spec(spec);spec.loader.exec_module(preview)
    systems=['erp','turismo'] if args.system=='both' else [args.system]
    output.mkdir(parents=True,mode=0o700);preview.RUNTIME=output
    preview.next_projects(dependencies=dependencies,systems=systems)
    results=[]
    env={**os.environ,'NEXT_TELEMETRY_DISABLED':'1','NEXT_PUBLIC_API_URL':'/api/v1','NEXT_PUBLIC_ENABLE_MOCKS':'false','CI':'1'}
    for system in systems:
        log=output/(system+'-build.log')
        with log.open('w') as stream:
            try:
                result=subprocess.run(['node',str(binary),'build','--webpack'],cwd=output/system,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=600)
                status='PASSED' if result.returncode==0 else 'FAILED'
            except subprocess.TimeoutExpired:status='TIMEOUT'
        results.append({'system':system,'status':status,'log':log.name,'strict_typescript':True,'source_tree_changed':False})
        print(json.dumps(results[-1]),flush=True)
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'production_ready':False,'scope':'Full generated Next source projects, no deployment','results':results,'dependencies':{'next':json.loads((dependencies/'next/package.json').read_text())['version']}}
    (output/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return 0 if all(row['status']=='PASSED' for row in results) else 1
if __name__=='__main__':raise SystemExit(main())
