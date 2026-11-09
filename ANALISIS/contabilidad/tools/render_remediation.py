"""Render exactly 20 evidence-linked execution work packages; no new global score."""
import argparse,json
from pathlib import Path
HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
def render(data):
    items=data['items'];ids=[r['id'] for r in items]
    if ids!=[f'H{i:02d}' for i in range(1,21)]:raise ValueError('Exactly 20 ordered unique work packages required.')
    coverage={a for r in items for a in r['accounting_items']}
    if coverage!={f'ACC-{i:03d}' for i in range(1,25)}:raise ValueError('Existing 24-item scope must remain covered.')
    lines=['# Plan autónomo de subsanación · 20 hitos','',
        'Estos 20 paquetes ordenan la ejecución de las mismas 24 tareas contables. No sustituyen el denominador global de 72 hitos ni añaden porcentaje por documentar un plan.',
        '', '**Modo de trabajo:** implementar una corrección concreta, ejecutar pruebas, conservar evidencia y continuar con el siguiente paquete habilitado. Un bloqueo externo deja registrado el requisito y permite avanzar en paquetes independientes. La automatización de pruebas no se presenta como implementación automática de código.',
        '', 'Los cambios locales reversibles ya están autorizados. Las aprobaciones de movimientos financieros, publicación y cuentas reales conservan sus reglas existentes. El 100 % requiere evidencias de los criterios completos, no solo archivos o simulaciones.',
        '', '| Hito | Frente | Estado | Dependencias |', '|---|---|---|---|']
    states={row['id']:row['state'] for row in items}
    counts={state:sum(row['state']==state for row in items) for state in ('VERIFICADO_LOCAL','EN_EJECUCION','PENDIENTE','BLOQUEADO_EXTERNO')}
    lines[2:2]=[f"Verificados localmente: **{counts['VERIFICADO_LOCAL']}/20** · En ejecución: **{counts['EN_EJECUCION']}** · Pendientes: **{counts['PENDIENTE']}**. Este conteo no equivale al porcentaje global ni a aceptación productiva.",'']
    for row in items:
        if row['state'] not in {'PENDIENTE','EN_EJECUCION','VERIFICADO_LOCAL','BLOQUEADO_EXTERNO'}:raise ValueError('Unknown execution state.')
        if any(dep not in ids[:ids.index(row['id'])] for dep in row['depends_on']):raise ValueError('Dependencies must point to preceding packages.')
        if row['state']=='VERIFICADO_LOCAL' and any(states.get(dep)!='VERIFICADO_LOCAL' for dep in row['depends_on']):raise ValueError('A verified package cannot have unverified dependencies.')
        if row['state']=='VERIFICADO_LOCAL' and not row['evidence']:raise ValueError('Verification requires evidence.')
        for ref in row['evidence']:
            path=(ROOT/ref).resolve()
            if not path.is_relative_to(ROOT) or not path.is_file():raise ValueError('Missing evidence.')
        lines.append(f"| {row['id']} | {row['title']} | {row['state']} | {', '.join(row['depends_on']) or 'Ninguna'} |")
    for row in items:
        lines+=['',f"## {row['id']} · {row['title']}",'',f"**Hallazgo:** {row['finding']}",'',f"**Corrección:** {row['action']}",'',f"**Resultado local actual:** {row.get('local_result','Pendiente de desarrollo/verificación local; consultar evidencia si existe.')}",'',f"**Cierre local verificable:** {row['acceptance']}",'',f"**Matriz original:** {', '.join(row['accounting_items'])}.", '', '**Requisitos externos:** '+('; '.join(row['external_gates']) or 'Ninguno para la corrección local descrita.'), '', '**Evidencia:** '+(', '.join(row['evidence']) or 'Pendiente; no se acredita cierre.')]
    return '\n'.join(lines)+'\n'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    text=render(json.loads((HERE/'plan-subsanacion-20.json').read_text()));path=HERE/'PLAN_SUBSANACION_20_HITOS.md'
    if args.check:
        if not path.exists() or path.read_text()!=text:raise SystemExit('Remediation plan is stale.')
    else:path.write_text(text)
    print('20 execution packages; 24 original tasks covered; global denominator unchanged.')
if __name__=='__main__':main()
