"""Deterministic, evidence-referenced milestone index; never estimates production readiness."""
import argparse,csv,json
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
HERE=ROOT/'ANALISIS/contabilidad'
STAGES=('functional_increment','automated_verification','full_acceptance')

def calculate(registry,rows):
    if registry.get('baseline')!='accounting-blueprint-v1':raise ValueError('Explicit baseline review required.')
    expected={r['id'] for r in rows}
    if len(expected)!=24 or len(rows)!=24:raise ValueError('The baseline requires exactly 24 unique work items; review the denominator explicitly.')
    entries=registry['items']
    if len(entries)!=24 or {r['id'] for r in entries}!=expected:raise ValueError('Progress items must match the approved matrix exactly.')
    points=0;accepted=0;details=[]
    for row in entries:
        if set(row['milestones'])!=set(STAGES):raise ValueError('Unknown or missing milestone.')
        completed=[]
        for stage in STAGES:
            evidence=row['milestones'][stage]
            if not isinstance(evidence,list):raise ValueError('Milestones require evidence lists, not a manually entered percentage.')
            for ref in evidence:
                if not isinstance(ref,str):raise ValueError('Invalid evidence reference.')
                target=(ROOT/ref).resolve()
                if not target.is_relative_to(ROOT) or not target.is_file():raise ValueError('Missing or out-of-scope evidence: '+ref)
            completed.append(bool(evidence))
        if completed[1] and not completed[0] or completed[2] and not all(completed[:2]):raise ValueError('Milestone dependencies are not satisfied.')
        score=sum(completed);points+=score;accepted+=int(completed[2])
        matrix=next(r for r in rows if r['id']==row['id'])
        details.append({'task':matrix['tarea'],'remaining':row.get('acceptance_remaining',matrix['limite']),'id':row['id'],'completed_milestones':score,'total_milestones':3,'full_acceptance':completed[2]})
    percent=(Decimal(points)*100/Decimal(72)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
    groups={
        'Núcleo y puente contable':['ACC-001','ACC-002','ACC-003','ACC-004','ACC-005','ACC-006','ACC-007','ACC-015'],
        'Comercial y fiscal':['ACC-008','ACC-009','ACC-014'],
        'Bóveda documental':['ACC-010','ACC-011'],
        'Operación y nómina':['ACC-012','ACC-013'],
        'Analítica financiera':['ACC-016','ACC-017'],
        'Sostenibilidad':['ACC-018','ACC-019'],
        'Asistencia y automatización':['ACC-020','ACC-021'],
        'Offline, rendimiento y operación':['ACC-022','ACC-023','ACC-024'],
    }
    by_id={r['id']:r for r in details};fronts=[]
    for name,identifiers in groups.items():
        done=sum(by_id[i]['completed_milestones'] for i in identifiers);total=3*len(identifiers)
        fronts.append({'front':name,'items':identifiers,'completed_milestones':done,'total_milestones':total,'implementation_percent':str((Decimal(done)*100/Decimal(total)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))})
    if sum(r['total_milestones'] for r in fronts)!=72 or len({i for r in fronts for i in r['items']})!=24:raise ValueError('Fronts must partition the unchanged baseline.')
    return {'fronts':fronts,'baseline':'accounting-blueprint-v1','measurement':'curated evidence-backed milestones, not effort or code coverage',
            'completed_milestones':points,'total_milestones':72,'implementation_percent':str(percent),
            'fully_accepted_items':accepted,'items_with_verified_increment':sum(r['completed_milestones']>=2 for r in details),'total_items':24,'production_ready':False,'items':details}

def render(result):
    return f'''# Avance verificable del motor de contabilidad

**Implementación y optimización: {result['implementation_percent']} %** · {result['completed_milestones']}/72 hitos.
**Alcance completo aceptado: {result['fully_accepted_items']}/24 tareas. Producción: no habilitada.**

La base es la directriz de siete pools y las 24 tareas de `matriz-pools.csv`. Cada tarea tiene tres hitos de igual peso:

1. Existe un incremento funcional ejecutable de la tarea, aunque su alcance todavía sea parcial.
2. Ese incremento dispone de verificación automatizada reproducible.
3. Se cumplen todos los criterios de aceptación de la tarea, incluidos ambos sistemas y las validaciones reales requeridas.

El máximo antes de aceptación completa de una tarea es 2/3. El porcentaje mide estos hitos, no líneas de código, horas, porcentaje de pruebas cubiertas ni ausencia de vulnerabilidades. No se obtiene crédito por documentación o planificación solas. El registro es una evaluación explícita de evidencias, no una deducción automática por presencia de archivos.

{result['items_with_verified_increment']} tareas tienen incrementos verificados; ninguna acredita aún su alcance completo. Reforzar pruebas existentes no aumenta automáticamente el porcentaje. El 100 % significará cumplimiento comprobado de esta versión del alcance, no perfección absoluta ni inmunidad a ataques.

| Frente | Hitos | Implementación verificable |
|---|---:|---:|
'''+''.join(f"| {r['front']} | {r['completed_milestones']}/{r['total_milestones']} | {r['implementation_percent']} % |\n" for r in result['fronts'])+'''
Los frentes agrupan las mismas 24 tareas sin duplicarlas ni cambiar el denominador. No son porcentajes de producción.

| Tarea | Hitos completados | Alcance completo aceptado |
|---|---:|---|
'''+''.join(f"| {r['id']} | {r['completed_milestones']}/3 | {'Sí' if r['full_acceptance'] else 'No'} |\n" for r in result['items'])+'''
Registro: `progress-registry.json`. Resultado calculado: `progreso.json`.
Regenerar con `python ANALISIS/contabilidad/tools/update_progress.py`; comprobar coherencia con `--check`.

Antes de cambiar el alcance o las ponderaciones se debe documentar una nueva base y conservar la anterior. Las acreditaciones de producción no se deducen del porcentaje.
'''

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    with (HERE/'matriz-pools.csv').open(newline='') as stream:rows=list(csv.DictReader(stream))
    result=calculate(json.loads((HERE/'progress-registry.json').read_text()),rows)
    outputs={HERE/'BLOQUEOS_POR_TAREA.md':'# Bloqueos para aceptación completa\n\n'+''.join(f"## {r['id']} · {r['task']}\n\n{r['completed_milestones']}/3 hitos. Pendiente: {r['remaining']}\n\n" for r in result['items']),HERE/'progreso.json':json.dumps(result,ensure_ascii=False,indent=2)+'\n',HERE/'PROGRESO.md':render(result)}
    outputs={path:content.rstrip()+"\n" for path,content in outputs.items()}
    if args.check:
        if any(not p.exists() or p.read_text()!=text for p,text in outputs.items()):raise SystemExit('Progress output is stale; regenerate after reviewing evidence.')
    else:
        for p,text in outputs.items():p.write_text(text)
    print(f"{result['implementation_percent']}% ({result['completed_milestones']}/72 milestones), full acceptance {result['fully_accepted_items']}/24")
if __name__=='__main__':main()
