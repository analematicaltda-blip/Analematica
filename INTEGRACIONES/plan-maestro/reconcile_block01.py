"""Associate bounded test evidence with requirements without claiming end-to-end completion."""
import argparse,csv,json
from collections import Counter
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--directory',type=Path,required=True);parser.add_argument('--runtime',type=Path,required=True);args=parser.parse_args()
    destination=args.directory/'runtime-evidence.json'
    if destination.exists():parser.error('Runtime evidence already attached; preserve it and use a new audit directory.')
    evidence=json.loads(args.runtime.read_text())
    if evidence.get('production_ready') is not False:parser.error('Expected an isolated contract report, not production certification.')
    suites={row['suite']:row for row in evidence['results']}
    rows=json.loads((args.directory/'matriz-funcional.json').read_text())
    links={
      'ANA-001':('corporate_gateway','Gateway probado con upstream simulado: autenticación/cookies/configuración. Dependencia real y panel propietario no acreditados.'),
      'ANA-003':('central_contract','Manifest autenticado probado en contrato aislado. No hay SSO de dominio ni recorrido integral de las tres interfaces.'),
      'ERP-020':('company_identity','Vista previa y borrador persistente verificados; disponibilidad, impuestos, aceptación y pagos pendientes.'),
      'ERP-044':('erp_customer','CRUD privado de clientes verificado; CRM completo y embudo pendientes.'),
      'ERP-045':('company_identity','Borradores privados e idempotentes; operación comercial/POS histórica permanece deshabilitada con503.'),
    }
    for row in rows:
        link=links.get(row['id'])
        if not link and row['estado']=='PARCIAL':link=('institutional_permissions',row['evidencia'])
        if link:
            suite,limit=link;result=suites.get(suite,{})
            row['evidencia_ejecucion_actual']=dict(suite=suite,status=result.get('status','NO_EJECUTADA'),tests=result.get('tests',0),limite=limit)
            if result.get('status')=='PASSED':row['estado']='PARCIAL';row['prueba_ejecutada']=True;row['evidencia']=limit
    destination.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    (args.directory/'matriz-priorizada.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    with (args.directory/'matriz-priorizada.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={'requirements':len(rows),'states':dict(Counter(row['estado'] for row in rows)),'suites_passed':sum(row['status']=='PASSED' for row in evidence['results']),'tests_passed':sum(row['tests'] for row in evidence['results'] if row['status']=='PASSED'),'all_end_to_end_verified':False}
    (args.directory/'cobertura.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary))
if __name__=='__main__':main()
