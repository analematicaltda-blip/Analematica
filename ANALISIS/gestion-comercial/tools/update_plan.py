"""Check declared commercial evidence and regenerate the fixed 24-task/72-milestone view.
This checks registry consistency; it never infers business acceptance from file presence.
"""
import argparse
import csv
import hashlib
import io
import json
from decimal import Context, Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIRECTORY = ROOT / 'ANALISIS/gestion-comercial'
SYSTEMS = {'sga-cd', 'erp-tur', 'analematica'}

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def check_evidence(reference, task_id, milestone_id):
    if not isinstance(reference, dict) or set(reference) != {'artifact', 'entry', 'entry_sha256'}:
        raise ValueError('Evidence reference must be explicit and hashed.')
    relative = Path(reference['artifact'])
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Evidence must remain in the repository.')
    source = ROOT / relative
    if source.is_symlink() or not source.resolve().is_relative_to(ROOT):
        raise ValueError('Evidence cannot escape the repository.')
    evidence = json.loads(source.read_text())
    for key in reference['entry'].split('.'):
        evidence = evidence[key]
    if hashlib.sha256(canonical(evidence)).hexdigest() != reference['entry_sha256']:
        raise ValueError('Evidence entry digest mismatch.')
    stage = (int(milestone_id.split('-')[1]) - 1) % 3
    task_ids = evidence.get('accepted_task_ids', []) if stage == 2 else evidence.get('verified_task_ids', evidence.get('accepted_task_ids', []))
    if task_id not in task_ids or milestone_id not in evidence['accepted_milestones']:
        raise ValueError('Evidence does not accept this task/milestone.')
    if set(evidence['systems']) != SYSTEMS:
        raise ValueError('Evidence must cover all three systems.')
    complete = evidence.get('acceptance_complete') is True
    # F and T are explicitly local stages. Do not require or invent external acceptance.
    if stage == 0 and not (complete or evidence.get('functional_scope_complete') is True):
        raise ValueError('Local functional scope is incomplete.')
    if stage == 1 and not (complete or (evidence.get('functional_scope_complete') is True and evidence.get('tests_complete') is True)):
        raise ValueError('Complete local functionality and tests are required.')
    if stage == 2 and not complete:
        raise ValueError('Integral acceptance is still pending.')

def measure(plan, checker=check_evidence):
    tasks = plan['tasks']
    if len(tasks) != 24 or [task['id'] for task in tasks] != [f'GC-{i:03d}' for i in range(1,25)]:
        raise ValueError('Keep the fixed 24-task scope and order.')
    if set(plan['systems']) != SYSTEMS:
        raise ValueError('All three systems are required.')
    seen = set(); completed = []; accepted = []
    for index, task in enumerate(tasks):
        if not set(task['dependencies']) <= seen or set(task['baseline']) != SYSTEMS:
            raise ValueError('Task dependency or system coverage mismatch.')
        seen.add(task['id'])
        milestones = task['milestones']
        if [row['id'] for row in milestones] != [f'GCH-{index*3+n:03d}' for n in (1,2,3)]:
            raise ValueError('Milestone identity changed or duplicated.')
        if [row['stage'] for row in milestones] != ['F', 'T', 'A']:
            raise ValueError('Preserve functionality, tests and acceptance stages.')
        done = []
        for milestone in milestones:
            if milestone['state'] not in {'PENDIENTE_DE_ACREDITACION','EN_EJECUCION','VERIFICADO'}:
                raise ValueError('Unknown milestone state.')
            verified = milestone['state'] == 'VERIFICADO'
            if verified:
                if not milestone['evidence']:
                    raise ValueError('Verified milestone needs evidence.')
                for reference in milestone['evidence']:
                    checker(reference, task['id'], milestone['id'])
                completed.append(milestone['id'])
            done.append(verified)
        if any(done[n] and not all(done[:n]) for n in range(1,3)):
            raise ValueError('No credit for later stages before their prerequisites.')
        if (task['state'] == 'COMPLETADA') != all(done):
            raise ValueError('Task completion and milestone acceptance must agree.')
        if all(done):
            accepted.append(task['id'])
    with localcontext(Context(prec=50)):
        percentage = format(Decimal(len(completed))*Decimal(100)/Decimal(72), '.2f')
    return {'tasks':24, 'milestones':72, 'fully_accepted_tasks':len(accepted),
            'accepted_task_ids':accepted, 'completed_milestones':len(completed),
            'completed_milestone_ids':completed, 'credited_milestone_percent':percentage,
            'production_enabled':False,
            'meaning':'Explicitly accepted milestones of this scope, not a production readiness or code-volume percentage.'}

def render_csv(plan):
    stream=io.StringIO(newline='');writer=csv.writer(stream)
    writer.writerow(['tarea','titulo','hito','etapa','estado','sga_cd_base','erp_base','analematica_base','faltante','aceptacion','dependencias','externos'])
    for task in plan['tasks']:
        for milestone in task['milestones']:
            writer.writerow([task['id'],task['title'],milestone['id'],milestone['stage'],milestone['state'],
                *[task['baseline'][system] for system in plan['systems']],task['missing'],task['acceptance'],
                ';'.join(task['dependencies']),';'.join(task['external_requirements'])])
    return stream.getvalue()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    plan_path=DIRECTORY/'plan-pool08.json';plan=json.loads(plan_path.read_text());result=measure(plan)
    plan['measurement'].update({key:result[key] for key in ('tasks','milestones','fully_accepted_tasks','completed_milestones','credited_milestone_percent')})
    plan['measurement']['implementation_percent']=result['credited_milestone_percent'] if plan['measurement']['baseline_review_complete'] else None
    outputs={plan_path:json.dumps(plan,ensure_ascii=False,indent=2)+'\n',
             DIRECTORY/'progreso-pool08.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n',
             DIRECTORY/'matriz-hitos-pool08.csv':render_csv(plan)}
    for path,content in outputs.items():
        if args.check:
            # Universal-newline reads need normalizing for the CSV writer's CRLF.
            if not path.exists() or path.read_text().replace('\r\n','\n') != content.replace('\r\n','\n'):
                raise SystemExit('Commercial plan output stale: '+path.name)
        else:
            path.write_text(content)
    print(f"{result['fully_accepted_tasks']}/24 tareas cerradas; {result['completed_milestones']}/72 hitos acreditados ({result['credited_milestone_percent']}%). Producción no habilitada.")

if __name__=='__main__':main()
