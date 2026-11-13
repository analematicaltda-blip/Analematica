"""Static evidence collection only: source presence never implies a working feature."""
import argparse,ast,json,csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SCOPES={'institucional':'BACKEND/SGA-TUR-BAKEND','erp':'BACKEND/SGA-ERP-TUR-BAKEND','corporativo':'BACKEND/ANALEMATICA-BACKEND','central':'BACKEND/SGA-CD-BACKEND/app'}
EXCLUDE={'agents','.git','__pycache__','node_modules','.runtime','private','staticfiles'}

def collect():
 result={'method':'static_ast_no_execution','runtime_verified':False,'scopes':SCOPES,'excluded_directory_names':sorted(EXCLUDE),'declared_permissions':[],'syntax_errors':[],'models':[],'routes':[],'pages':[],'python_counts':{}}
 for system,folder in SCOPES.items():
  count=0
  for file in sorted((ROOT/folder).rglob('*.py')):
   if file.is_symlink():continue
   rel=file.relative_to(ROOT/folder)
   if set(rel.parts)&EXCLUDE or (system in {'central','corporativo'} and 'agents' in rel.parts):continue
   count+=1;name=str(file.relative_to(ROOT))
   try:tree=ast.parse(file.read_bytes())
   except (SyntaxError,UnicodeError) as error:result['syntax_errors'].append({'platform':system,'path':name,'line':getattr(error,'lineno',None),'reason':getattr(error,'msg',type(error).__name__)});continue
   for node in ast.walk(tree):
    if isinstance(node,ast.ClassDef):
     declarations={}
     for item in node.body:
      if isinstance(item,ast.Assign):
       for target in item.targets:
        if isinstance(target,ast.Name) and target.id in {'permission_classes','authentication_classes'}:declarations[target.id]=ast.unparse(item.value)
     if declarations:result['declared_permissions'].append({'platform':system,'class':node.name,'path':name,'line':node.lineno,'declared_only':True,**declarations})
     fields=[]
     for field in node.body:
      if isinstance(field,ast.Assign) and isinstance(field.value,ast.Call):
       kind=ast.unparse(field.value.func)
       if kind.startswith('models.'):
        fields.append({'name':ast.unparse(field.targets[0]),'kind':kind,'related_model':ast.unparse(field.value.args[0]) if field.value.args and any(t in kind for t in ['ForeignKey','OneToOneField','ManyToManyField']) else None})
     if fields:result['models'].append({'platform':system,'name':node.name,'path':name,'line':node.lineno,'fields':fields})
    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
     for decorator in node.decorator_list:
      if isinstance(decorator,ast.Call) and isinstance(decorator.func,ast.Attribute) and ast.unparse(decorator.func.value) in {'app','router','api_router'} and decorator.func.attr in {'get','post','put','patch','delete','api_route'} and decorator.args and isinstance(decorator.args[0],ast.Constant) and isinstance(decorator.args[0].value,str):
       result['routes'].append({'platform':system,'route_fragment':decorator.args[0].value,'path':name,'line':decorator.lineno,'resolved':False,'decorator_method':decorator.func.attr})
    if isinstance(node,ast.Call) and ast.unparse(node.func) in {'path','re_path','router.register'} and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):result['routes'].append({'platform':system,'route_fragment':node.args[0].value,'path':name,'line':node.lineno,'resolved':False})
  result['python_counts'][system]=count
 for system,folder in [('institucional','FRONTEND/SGA-TUR-FRONTEND'),('erp','FRONTEND/SGA-ERP-TUR-FRONTEND'),('corporativo','FRONTEND/ANALEMATICA-FRONTEND')]:
  for file in sorted((ROOT/folder).rglob('*')):
   if (file.name in {'page.tsx','layout.tsx'} or (system=='corporativo' and file.suffix=='.html')) and not(set(file.relative_to(ROOT/folder).parts)&EXCLUDE):result['pages'].append({'platform':system,'path':str(file.relative_to(ROOT)),'kind':file.name,'runtime_verified':False})
 return result

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();r=collect();args.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print('Source inventory:',r['python_counts'],'models:',len(r['models']),'route fragments:',len(r['routes']),'pages/layouts:',len(r['pages']),'syntax errors:',len(r['syntax_errors']))
if __name__=='__main__':main()
