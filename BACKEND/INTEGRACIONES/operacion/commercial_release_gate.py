"""Read-only closure gate. Evidence integrity is not provider/physical acceptance."""
import importlib.util,json,argparse,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def evaluate():
 path=ROOT/'ANALISIS/gestion-comercial/tools/update_plan.py';spec=importlib.util.spec_from_file_location('commercial_progress_gate',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);plan=json.loads((ROOT/'ANALISIS/gestion-comercial/plan-pool08.json').read_text());progress=m.measure(plan)
 blockers=[{'task':task['id'],'state':task['state'],'unverified':[row['id'] for row in task['milestones'] if row['state']!='VERIFICADO']} for task in plan['tasks'] if any(row['state']!='VERIFICADO' for row in task['milestones'])]
 return {'schema':'commercial-release-gate-v1','plan_sha256':hashlib.sha256((ROOT/'ANALISIS/gestion-comercial/plan-pool08.json').read_bytes()).hexdigest(),'progress':progress,'blockers':blockers,'all_72_milestones_evidenced':not blockers,'production_enabled':False,'publication_performed':False,'gate':'BLOCKED' if blockers else 'REQUIRES_SEPARATE_PRODUCTION_APPROVAL','limitations':['Hashes verify internal evidence consistency, not authenticity of external acceptance','No SLA, infrastructure, providers, keys or physical device qualification inferred from local test counts']}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args();r=evaluate()
 if a.output:
  with a.output.open('x') as f:json.dump(r,f,ensure_ascii=False,indent=2)
 print(json.dumps({'gate':r['gate'],'milestones':r['progress']['completed_milestones'],'blocked_tasks':len(r['blockers']),'production_enabled':False}))
