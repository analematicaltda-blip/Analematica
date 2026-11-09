"""Validate the remaining-work backlog structure, not fiscal/production acceptance."""
import json
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
ROOT=HERE.parents[1]

def main():
    data=json.loads((HERE/'PLAN_REMANENTE_20_HITOS.json').read_text())
    rows=data['items'];ids=[r['id'] for r in rows];order=data['execution_order']
    if ids!=[f'R{i:02d}' for i in range(1,21)] or len(order)!=20 or set(order)!=set(ids):raise ValueError('Exactly20 unique ordered tasks required.')
    if data['baseline_total_milestones']!=72 or not data['new_plan_does_not_reset_progress']:raise ValueError('Preserve original accounting denominator.')
    percent=(Decimal(data['baseline_completed_milestones'])*100/72).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)
    if str(percent)!=data['baseline_percent']:raise ValueError('Inconsistent baseline percentage.')
    prior=json.loads((HERE/'plan-subsanacion-20.json').read_text());prior_ids={r['id'] for r in prior['items']}
    for row in rows:
        if not row['previous_packages'] or set(row['previous_packages'])-prior_ids:raise ValueError('Explicit previous scope mapping required.')
        if any(order.index(dep)>=order.index(row['id']) for dep in row['depends_on']):raise ValueError('Dependency cycle or invalid execution order.')
        if row['code_state'] not in {'PENDIENTE','EN_EJECUCION','VERIFICADO_LOCAL'}:raise ValueError('Unknown code state.')
        if row['acceptance_state'] not in {'PENDIENTE','VERIFICADO_LOCAL','ACEPTADO_COMPLETO'}:raise ValueError('Unknown acceptance state.')
        if row['code_state']=='VERIFICADO_LOCAL' and not row['evidence']:raise ValueError('Verification references required.')
        if row['fully_closed'] and (row['code_state']!='VERIFICADO_LOCAL' or row['acceptance_state']=='PENDIENTE' or row['external_gates'] and row['acceptance_state']!='ACEPTADO_COMPLETO'):raise ValueError('Cannot close a partial or externally unaccepted task.')
        for ref in row['evidence']:
            path=(ROOT/ref).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():raise ValueError('Missing or external evidence reference.')
        if not all(isinstance(row[key],str) and row[key].strip() for key in ['finding','implementation','local_acceptance']):raise ValueError('Finding, correction and closing test required.')
    if data['all_20_closed']!=all(r['fully_closed'] for r in rows):raise ValueError('Do not assert20 closures without individual acceptance.')
    if data['production_ready'] and not data['all_20_closed']:raise ValueError('Production cannot be inferred from a partial plan.')
    print('20 remaining tasks validated; baseline preserved; references/structure checked, not professional or production acceptance.')
if __name__=='__main__':main()
