"""Static evidence collection only: source presence never implies a working feature."""
import argparse,ast,json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SCOPES={'institucional':'BACKEND/SGA-TUR-BAKEND','erp':'BACKEND/SGA-ERP-TUR-BAKEND','corporativo':'BACKEND/ANALEMATICA-BACKEND/deployment','central':'BACKEND/SGA-CD-BACKEND/app'}
EXCLUDE={'.git','__pycache__','node_modules','.runtime','private','staticfiles'}

def collect():
 result={'method':'static_ast_no_execution','runtime_verified':False,'scopes':SCOPES,'excluded_directory_names':sorted(EXCLUDE),'syntax_errors':[],'models':[],'routes':[],'pages':[],'python_counts':{}}
 for system,folder in SCOPES.items():
  count=0
  for file in sorted((ROOT/folder).rglob('*.py')):
   rel=file.relative_to(ROOT/folder)
   if set(rel.parts)&EXCLUDE or (system=='central' and 'agents' in rel.parts):continue
   count+=1;name=str(file.relative_to(ROOT))
   try:tree=ast.parse(file.read_bytes())
   except (SyntaxError,UnicodeError) as error:result['syntax_errors'].append({'platform':system,'path':name,'line':getattr(error,'lineno',None),'reason':getattr(error,'msg',type(error).__name__)});continue
   for node in ast.walk(tree):
    if isinstance(node,ast.ClassDef):
     fields=[]
     for field in node.body:
      if isinstance(field,ast.Assign) and isinstance(field.value,ast.Call):
       kind=ast.unparse(field.value.func)
       if kind.startswith('models.'):
        fields.append({'name':ast.unparse(field.targets[0]),'kind':kind,'related_model':ast.unparse(field.value.args[0]) if field.value.args and any(t in kind for t in ['ForeignKey','OneToOneField','ManyToManyField']) else None})
     if fields:result['models'].append({'platform':system,'name':node.name,'path':name,'line':node.lineno,'fields':fields})
    if isinstance(node,ast.Call) and ast.unparse(node.func) in {'path','re_path','router.register'} and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):result['routes'].append({'platform':system,'route_fragment':node.args[0].value,'path':name,'line':node.lineno,'resolved':False})
  result['python_counts'][system]=count
 for system,folder in [('institucional','FRONTEND/SGA-TUR-FRONTEND'),('erp','FRONTEND/SGA-ERP-TUR-FRONTEND')]:
  for file in sorted((ROOT/folder).rglob('*')):
   if file.name in {'page.tsx','layout.tsx'} and not(set(file.relative_to(ROOT/folder).parts)&EXCLUDE):result['pages'].append({'platform':system,'path':str(file.relative_to(ROOT)),'kind':file.name,'runtime_verified':False})
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();r=collect();args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('Source inventory:',r['python_counts'],'models:',len(r['models']),'route fragments:',len(r['routes']),'pages/layouts:',len(r['pages']),'syntax errors:',len(r['syntax_errors']))
if __name__=='__main__':main()
