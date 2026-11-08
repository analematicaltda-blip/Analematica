/* Source parser only. Successful parsing does not certify types, routes or APIs. */
const fs=require('node:fs'),path=require('node:path');
const args=process.argv.slice(2);const option=name=>args[args.indexOf(name)+1];
if(!args.includes('--dependencies')||!args.includes('--output'))throw Error('Use --dependencies node_modules --output new-report.json');
const ts=require(path.resolve(option('--dependencies'),'typescript'));
const output=path.resolve(option('--output'));if(fs.existsSync(output))throw Error('Preserve prior evidence; use a new output file');
const root=path.resolve(__dirname,'../..');
const scopes={analematica:'FRONTEND/ANALEMATICA-FRONTEND',erp:'FRONTEND/SGA-ERP-TUR-FRONTEND',turismo:'FRONTEND/SGA-TUR-FRONTEND/src'};
const excluded=new Set(['agents','node_modules','.git','.runtime','.next','dist','build','private','tests']);
const result={scope:'Static syntax only; no source execution',production_ready:false,typescript:ts.version,files:{},errors:[],page_contract_warnings:[]};
function walk(directory){return fs.readdirSync(directory,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(entry=>{const target=path.join(directory,entry.name);if(entry.isSymbolicLink()||excluded.has(entry.name))return [];return entry.isDirectory()?walk(target):/\.(tsx?|jsx?|mjs)$/.test(entry.name)?[target]:[];});}
for(const [system,folder] of Object.entries(scopes)){
 const files=walk(path.join(root,folder));result.files[system]=files.length;
 for(const filename of files){const source=ts.createSourceFile(filename,fs.readFileSync(filename,'utf8'),ts.ScriptTarget.Latest,true,filename.endsWith('.tsx')?ts.ScriptKind.TSX:filename.endsWith('.ts')?ts.ScriptKind.TS:filename.endsWith('.jsx')?ts.ScriptKind.JSX:ts.ScriptKind.JS);
  if(path.basename(filename)==='page.tsx'){
   const hasDefault=source.statements.some(node=>ts.isExportAssignment(node)&&!node.isExportEquals||node.modifiers?.some(modifier=>modifier.kind===ts.SyntaxKind.DefaultKeyword)||ts.isExportDeclaration(node)&&node.exportClause&&ts.isNamedExports(node.exportClause)&&node.exportClause.elements.some(element=>element.name.text==='default'));
   if(!hasDefault)result.page_contract_warnings.push({system,path:path.relative(root,filename),issue:'PAGE_WITHOUT_DEFAULT_EXPORT'});
  }
  for(const diagnostic of source.parseDiagnostics){const pos=source.getLineAndCharacterOfPosition(diagnostic.start||0);result.errors.push({system,path:path.relative(root,filename),line:pos.line+1,column:pos.character+1,code:diagnostic.code,message:ts.flattenDiagnosticMessageText(diagnostic.messageText,' ')});}
 }
}
fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(JSON.stringify({files:result.files,syntax_errors:result.errors.length,page_contract_warnings:result.page_contract_warnings.length,report:output}));process.exitCode=result.errors.length?1:0;
