"""Reproducible three-system source audit; never labels source presence as operational."""
import argparse,csv,hashlib,importlib.util,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SOURCES={'Analematica':['BACKEND/ANALEMATICA-BACKEND','FRONTEND/ANALEMATICA-FRONTEND'],'SGA-ERP-TUR':['BACKEND/SGA-ERP-TUR-BAKEND','FRONTEND/SGA-ERP-TUR-FRONTEND'],'SGA-TUR':['BACKEND/SGA-TUR-BAKEND','FRONTEND/SGA-TUR-FRONTEND']}
EXCLUDE={'.git','agents','node_modules','__pycache__','.next','dist','build','.runtime','private','staticfiles'}

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def collect():
    inventory=module('source_inventory',Path(__file__).resolve().parents[3] / 'BACKEND/INTEGRACIONES/turismo-erp/inventory.py').collect()
    inventory['source_hashes']={};duplicates=defaultdict(list);counts={};manifests=[]
    for system,folders in SOURCES.items():
        count=Counter()
        for folder in folders:
            directory=ROOT/folder
            for path in sorted(directory.rglob('*')):
                if not path.is_file() or path.is_symlink() or set(path.relative_to(directory).parts)&EXCLUDE:continue
                if path.suffix not in {'.py','.ts','.tsx','.js','.jsx','.html','.css','.mjs'}:continue
                name=str(path.relative_to(ROOT));digest=hashlib.sha256(path.read_bytes()).hexdigest()
                inventory['source_hashes'][name]=digest;count[path.suffix]+=1
                if path.stat().st_size>100:duplicates[digest].append(name)
            for name in ('package.json','requirements.txt','pyproject.toml','next.config.ts','vite.config.ts'):
                path=directory/name
                if path.is_file():manifests.append({'system':system,'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        counts[system]=dict(count)
    inventory['three_system_source_counts']=counts
    inventory['manifests']=manifests
    inventory['exact_duplicate_source_groups']=[{'sha256':digest,'paths':paths,'action':'REVISAR_DEPENDENCIAS_NO_ELIMINAR'} for digest,paths in sorted(duplicates.items()) if len(paths)>1]
    inventory['limits']=['Route fragments are not resolved endpoints','Declared permissions are not effective authorization','Identical sources are candidates, not safely removable duplicates','No databases, secrets or production services inspected']
    rows=module('functional_requirements',Path(__file__).resolve().parents[3] / 'BACKEND/INTEGRACIONES/turismo-erp/make_matrix.py').generate()
    for row in rows:
        row['responsable']='Arquitectura / auditoría funcional'
        row['dependencia']='Entorno aislado y datos de prueba; identidad y alcance del dominio'
        row['evidencia_ejecucion_actual']='Pendiente de asociar una prueba integral; conservar límites de evidencia histórica.'
    for index,(feature,path,priority) in enumerate([
        ('Gateway y aislamiento de cookies','BACKEND/ANALEMATICA-BACKEND/deployment/api.py','CRITICA'),
        ('Ingreso real y panel del propietario','FRONTEND/ANALEMATICA-FRONTEND/admin.html','CRITICA'),
        ('Manifest de sistemas e identidad','FRONTEND/ANALEMATICA-FRONTEND/platform.html','ALTA'),
        ('Reportes institucionales completos','BACKEND/ANALEMATICA-BACKEND/services/gov_reports.py','ALTA'),
        ('Navegación y diseño responsive','FRONTEND/ANALEMATICA-FRONTEND','ALTA'),
        ('Integración empresarial y módulos contables','BACKEND/ANALEMATICA-BACKEND/core_erp','CRITICA')],1):
        rows.append({'id':f'ANA-{index:03}','plataforma':'ANA','modulo':'Corporativo','funcionalidad':feature,'ruta_o_componente':path,'estado':'DEFECTUOSA' if index==4 else 'NO VERIFICADA','evidencia':'El archivo no compila; contiene expresiones incompletas. Activación en runtime no acreditada.' if index==4 else 'Fuente candidata; probar alcance descrito antes de certificarlo.','riesgo':'Confundir disponibilidad de fuentes con procesos autorizados operativos.','prioridad':priority,'accion':'Revisar dependencia y ejecutar aceptación acotada.','criterio_aceptacion':'Ingreso y flujo real con autorización positiva y negativa; no filtrar datos ni alterar módulos previos.','prueba_ejecutada':False,'responsable':'Arquitectura / auditoría funcional','dependencia':'SGA-CD y configuración aislada para el gateway','evidencia_ejecucion_actual':'Pendiente de asociar resultado runtime con su alcance exacto.'})
    return inventory,rows

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--directory',type=Path,required=True);args=parser.parse_args()
    if args.directory.exists():parser.error('Use a new output directory; prior audit evidence is preserved.')
    inventory,rows=collect();args.directory.mkdir(parents=True)
    (args.directory/'inventario.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
    (args.directory/'matriz-funcional.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    with (args.directory/'matriz-funcional.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summary={'runtime_verified':False,'python_counts':inventory['python_counts'],'models':len(inventory['models']),'route_fragments':len(inventory['routes']),'pages_layouts':len(inventory['pages']),'permission_declarations':len(inventory['declared_permissions']),'exact_duplicate_groups':len(inventory['exact_duplicate_source_groups']),'syntax_findings':inventory['syntax_errors'],'requirements':len(rows),'states':dict(Counter(row['estado'] for row in rows))}
    (args.directory/'resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
